from openai import OpenAI
from pydantic import BaseModel
import textwrap
import os

os.environ["OPENAI_API_KEY"]='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'
client = OpenAI()



query ="""What can you tell me about the current mayor of Cobourg"""

response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search_preview", 
            "user_location": {
            "type": "approximate",
            "country": "CA",
            "city": "Cobourg",
            "region": "Ontario"
        }
        }   ],
    input=query
)



print('\n', query )


print('\n',textwrap.fill(response.output_text, width=100))
