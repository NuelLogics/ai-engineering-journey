import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)  # automatically finds OPENAI_API_KEY from the environment


response = client.responses.create(
    model="openai/gpt-oss-120b",
    input="What is Software Engineering in one sentence to an untechnical man?",
    temperature=0.7,
    max_output_tokens=100,
)
print(response.output_text)
