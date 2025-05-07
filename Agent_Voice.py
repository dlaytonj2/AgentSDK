import asyncio
import numpy as np 


from agents import Agent
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
)
from voiceutil import AudioPlayer, record_audio

import os  
os.environ["OPENAI_API_KEY"]='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'

"""
This is a simple example that uses a recorded audio buffer. 

1. You can record an audio clip in the terminal.
2. The pipeline automatically transcribes the audio.
3. The agent workflow is a simple one that starts at the Assistant agent.
4. The output of the agent is streamed to the audio player.

Try examples like:
- Tell me a joke (will respond with a joke)
- Say something in French and it will respond in French 
"""

french_agent = Agent(
    name="French",
    handoff_description="A French speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in French only.",
    ),
    model="gpt-4o-mini",
)

Assistant_agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in French, handoff to the french agent.",
    ),
    model="gpt-4o-mini",
    handoffs=[french_agent]
)


class WorkflowCallbacks(SingleAgentWorkflowCallbacks):
    def on_run(self, workflow: SingleAgentVoiceWorkflow, transcription: str) -> None:
        print(f"[debug] on_run called with transcription: {transcription}")


async def main():

    '''An opinionated voice agent pipeline. It works in three steps: 
    1. Transcribe audio input into text. 
    2. Run the provided workflow, which produces a sequence of text responses. 
    3. Convert the text responses into streaming audio output.'''

    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(Assistant_agent, callbacks=WorkflowCallbacks())
    )

    audio_input = AudioInput(buffer=record_audio())
   
    result = await pipeline.run(audio_input)


    with AudioPlayer() as player:
        async for event in result.stream():

            print(f'Pipeline finished, playing back result ... \n event type:{event}')
            
            if event.type == "voice_stream_event_audio":
                player.add_audio(event.data)
                print("Received audio")
            elif event.type == "voice_stream_event_lifecycle":
                print(f"Received lifecycle event: {event.event}")

        # Add 1 second of silence to the end of the stream to avoid cutting off the last audio.
        player.add_audio(np.zeros(24000 * 1, dtype=np.int16))

if __name__ == "__main__":
    asyncio.run(main())