from openai import OpenAI
import os
import textwrap
import time

os.environ["OPENAI_API_KEY"]='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'
client = OpenAI()


''' (1) Create a Vector Store with one or more documents'''

vector_store_name = "Twenty Thousand Leagues Under the Sea"
file_ids = []

file = client.files.create(
  file=open( "./TextFiles/JVTwentyThousand.txt", "rb"),
  purpose='assistants'
)
file_ids.append(file.id)

# Create a vector store of one or more documents 
vector_store = client.vector_stores.create(name=vector_store_name,file_ids=file_ids)
 
print('Vector Store Created', vector_store.id)


# Sleep for a minute to allow time for vector store processing
print("Waiting for 30 seconds to allow vector store processing...")
time.sleep(30)  
print("Wait complete. Proceeding with query...")


query ="""Review the story in the vector store provided. 
Base your answers only on this vector store. 
Identify the prinicpal characters and the protagonist. 
If there is no protagonist, then explain further."""

response = client.responses.create(
    model="gpt-4o",
    input= query,
    tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}],
)
print('\n', query )
print('\n',textwrap.fill(response.output_text, width=80))