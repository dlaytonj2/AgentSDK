import asyncio

import os
os.environ["OPENAI_API_KEY"]='Your OpenAI API key goes here'

from agents import Agent, ItemHelpers, Runner, trace

"""
This example shows the parallelization pattern. We run the agent three times in parallel, and pick
the best result.
"""


poet_agent = Agent(
    name="poet_agent",
    instructions='''For the topic provided. Create a non-rhyming free verse poem. Give the poem a title''',
)

poem_picker = Agent(
    name="poem_picker",
    instructions= '''You are an expert judge of poetry. Read all of the poems and then select the best poem. 
    Provide the reasons for your choice referencing the other poems''',
)


async def Many_Poets(msg):
    

    # Ensure the entire workflow is a single trace
    with trace("Parallel Poetry"):
        res_1, res_2, res_3 = await asyncio.gather(
            Runner.run(
                poet_agent,
                msg,
            ),
            Runner.run(
                poet_agent,
                msg,
            ),
            Runner.run(
                poet_agent,
                msg,
            ),
        )

        print('\n res_1.new_items: \n', res_1.new_items, 
              '\n res_1 \n', res_1.final_output,
              '\n ItemHelpers.text_message_outputs: \n ',ItemHelpers.text_message_outputs(res_1.new_items))

        outputs = [
            ItemHelpers.text_message_outputs(res_1.new_items),
            ItemHelpers.text_message_outputs(res_2.new_items),
            ItemHelpers.text_message_outputs(res_3.new_items),
        ]

       



        poems = ""
        for i, poem in enumerate(outputs, 1):    
        # Create a string with all poems for the picker agent
            poems += f"Poem {i}:\n{poem}\n\n"

        print(f'\n Poems: {poems}')
              
        best_poem = await Runner.run(
            poem_picker,
            f"Input: {msg}\n\n Poems:\n {poems}",
        )

    print("\n\n" + "-" * 60)

    print(f"\nBest Poem and reasons for selecting: {best_poem.final_output}")


if __name__ == "__main__":

    msg = ''' The plight of the homeless on a cold winter night in a big city'''

    asyncio.run(Many_Poets(msg))