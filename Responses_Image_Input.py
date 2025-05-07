from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"]='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'

client = OpenAI()

import base64
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Set the path to your input image 
image_path = "./images/accident1.jpeg"
base64_image = encode_image(image_path)
image_url = f"data:image/jpeg;base64,{base64_image}"
# Set your prompt
prompt = '''You are an expert insurance claims investigator. Describe the incident in this 
picture in as much detail as you can. Provide a probable determination on whether personal injury was involved.
Determine location of incicent if you can '''


response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt },
                {"type": "input_image", "image_url": image_url}                    
            ]
        }
    ]
)

print(response.output_text)
