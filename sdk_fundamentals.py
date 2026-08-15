import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads .env and loads OPENAI_API_KEY into the environment

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)  # automatically finds OPENAI_API_KEY from the environment


# --- Test 1: System role in action ---
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a pirate. Respond only in pirate speak.",
        },
        {"role": "user", "content": "What is AI Engineering?"},
    ],
    temperature=0.7,
    max_tokens=150,
)


print("=== Test 1: System role ===")


print(response.choices[0].message.content)


# --- Test 2: Multi-turn conversation ---
response2 = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful Python tutor."},
        {
            "role": "user",
            "content": "How do you explain OpenAI Python SDK to someone new to programming?",
        },
        {
            "role": "assistant",
            "content": "The OpenAI Python SDK is a library that allows you to easily integrate OpenAI's language model into your Python applications.",
        },
        {"role": "user", "content": "Give me a one-line example."},
    ],
    temperature=0.0,  # deterministic — factual answer
    max_tokens=60,
)
print("\n=== Test 2: Multi-turn ===")
print(response2.choices[0].message.content)
