from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)

models = client.models.list()

for model in models.data:
    print(model.id)
# ------------------------------------------------------------------------------


response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
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
    max_tokens=100,
)
print("\n=== Test 2: Multi-turn ===")
print(response.choices[0].message.content)


# -----------------------------------------------------------------------------------


response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "You are a Catholic Priest and scientist. Respond only in priest speak.",
        },
        {"role": "user", "content": "What is AI Engineering?"},
        {
            "role": "assistant",
            "content": "Yes, AI Engineering is different from ML Engineering. Most people mix that up. Want me to explain the difference? and how they relate to each other?",
        },
    ],
    temperature=0.7,
    max_tokens=100,
)


print(response.choices[0].message.content)
