from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"]='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'
client = OpenAI()


poet_response = client.responses.create(
    model="gpt-4o-mini",
    input="Write a haiku about a frog in a pond",
)
print(f'\n First draft of poem: \n\n {poet_response.output_text}')

print('\n Critic is reviewing...\n')
critic_response = client.responses.create(
    model="gpt-4o-mini",
    previous_response_id=poet_response.id,
    input=[{"role": "user", "content": """Review the haiku and provide feedback on how it might be improved.
            Do not rewrite the poem. All output should be concise and in plain text only"""}],
)
print(f'\n Critics Response:\n\n {critic_response.output_text}')

print('\n Poet is rewriting the poem...\n')
poet_response = client.responses.create(
    model="gpt-4o-mini",
    previous_response_id=critic_response.id,
    input=[{"role": "user", "content":"Rewrite the haiku using feedback from critic"}]
)
print(f'\n Rewritten Poem:\n\n {poet_response.output_text}')
