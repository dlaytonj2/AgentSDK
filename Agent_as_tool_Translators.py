import asyncio

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace

"""
This example shows the agents-as-tools pattern. The frontline agent receives a user message and
then picks which agents to call, as tools. In this case, it picks from a set of translation
agents. It then ensures the translations are corect 
"""

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You translate the user's message from Spanish to English",
    handoff_description="An Spanish to English translator",
)

french_agent = Agent(
    name="french_agent",
    instructions="You translate the user's message from French to English",
    handoff_description="An French to English translator",
)

italian_agent = Agent(
    name="italian_agent",
    instructions="You translate the user's message from Italian to English",
    handoff_description="An Italian to English translator",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=
        '''You are a translation agent. You use the tools given to you to translate.
        If asked for multiple translations, you call the relevant tools in order.
        You never translate on your own, you always use the provided tools.
        If you can't translate some of the text, just say so. 
        Your final output will be in English'''
    ,
   
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_Spanish_to_English",
            tool_description="Translate the user's message Spanish to English",
        ),
        french_agent.as_tool(
            tool_name="translate_French_to_English",
            tool_description="Translate the user's message from French to English",
        ),
        italian_agent.as_tool(
            tool_name="translate_Italian_to_English",
            tool_description="Translate the user's message from Italian to English",
        ),
    ],
)

synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions='''You inspect translations, correct them if needed, 
    and produce a final concatenated response.''',
)


async def Translator():
    msg = '''La pioggia in Spagna cade principalmente sulla pianura. 
 La pluie en Espagne tombe principalement sur la plaine. 
 La lluvia en España cae principalmente en la llanura.
 De regen in Spanje valt voornamelijk op de vlakte.'''

    print(f'\n The text to be translated is: \n {msg}')

    # Run the entire orchestration in a single trace
    with trace("Orchestrator evaluator"):
        orchestrator_result = await Runner.run(orchestrator_agent, msg)

        for item in orchestrator_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"\n  - Translation step: \n {text}")
        
        print(f'\n orchestrator to input list:\n {orchestrator_result.to_input_list()}')
        print(f'\n orchestrator final output:\n {orchestrator_result.final_output}')
        
        synthesizer_result = await Runner.run(
            synthesizer_agent, orchestrator_result.to_input_list()
        )

    print(f"\n\n Final response of synthesizer:\n{synthesizer_result.final_output}")

if __name__ == "__main__":
    asyncio.run(Translator())