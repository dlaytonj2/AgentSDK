from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"]='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'
client = OpenAI()


vector_store_name = "JulesVerne"

print('\n Creating a vector store...')

# Create a vector store of one or more documents 
vector_store = client.vector_stores.create(name=vector_store_name)
 

# Ready the files for upload to OpenAI 
file_paths = ["./TextFiles/JVTwentyThousand.txt"]

file_streams = [open(path, "rb") for path in file_paths]

print('\n File Streams:', file_streams)
# Use the upload and poll to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.

file_batch = client.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# You can print the status and the file counts of the batch to see the result of this operation. 
print("\n File Batch Status:",file_batch.status)
print("\n File Batch Counts:",file_batch.file_counts)

print('Finished', vector_store.id)


