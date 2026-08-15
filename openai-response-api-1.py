# from openai import OpenAI

# client = OpenAI()

# response = client.responses.create(
#     model="...", input="Explain what an API is in one sentence."
# )

# print(response.output_text)

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads .env and loads OPENAI_API_KEY into the environment

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)  # automatically finds OPENAI_API_KEY from the environment

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Explain what an API is in one sentence."}],
)

print(response.choices[0].message.content)
