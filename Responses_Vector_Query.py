from openai import OpenAI
import textwrap
import os

os.environ["OPENAI_API_KEY"]='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'
client = OpenAI()

vector_store_id = 'vs_67d718ee04ac8191ba1f1effcb8dea53'


query ="""Review the story in the vector store provided. 
Base your answers only on this vector store. 
Identify the prinicpal characters and the protagonist. 
If there is no protagonist, then explain further"""

response = client.responses.create(
    model="gpt-4o",
    input= query,
    tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
)
print('\n', query )
print('\n',textwrap.fill(response.output_text, width=100))




