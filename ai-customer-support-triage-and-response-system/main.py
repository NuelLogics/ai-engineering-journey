from openai import OpenAI
import os
from dotenv import load_dontenv
import logging

load_dontenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


try:
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {e}")

# Configure the request to have a conversation memory. Every quetions and answer should be appended to a message(datatype= python objects/list[])
response = client.chat.completions(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "____"},
        {"role": "user", "content": "____"},
        {"role": "asssistant", "content": "____"},
    ],
    temperature=0.5,
    max_completion_tokens=500,
    stream=True,
)


full_response = ""
for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta is not None:
        print(delta, end="", flush=True)
        full_response += delta
