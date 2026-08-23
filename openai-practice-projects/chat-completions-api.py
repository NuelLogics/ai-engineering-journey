from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)
# -------Commented out code to list all available models in the Groq API. Uncomment to use.-------
# models = client.models.list()

# for model in models.data:
#     print(model.id)
# ------------------------------------------------------------------------------


def chat(system_prompt, user_message, temperature=0.7, max_tokens=500):
    """Chat Completions wrapper — universal, works with any provider."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    finish = response.choices[0].finish_reason
    if finish == "length":
        print(
            f"⚠️  Response cut off — raise max_tokens (used {response.usage.completion_tokens})"
        )

    print(
        f"[chat] tokens: {response.usage.prompt_tokens}in "
        f"+ {response.usage.completion_tokens}out "
        f"= {response.usage.total_tokens}total"
    )

    return response.choices[0].message.content


chat_response = chat(
    system_prompt="You are a concise assistant.",
    user_message="What is a neural network in one sentence?",
)


print(chat_response)
