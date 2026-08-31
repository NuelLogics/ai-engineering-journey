import os
import logging

from openai import OpenAI
from dotenv import load_dotenv
from data import Contexts


load_dotenv()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
)


try:
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {e}")


message = [
    {
        "role": "system",
        "content": f"You are a helpful assistant for Sckye Hospital. Context: {Contexts}",
    }
]

while True:
    incoming_message = input("You: ")
    message.append({"role": "user", "content": incoming_message})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=message,
            temperature=0.5,
            max_completion_tokens=500,
            stream=True,
        )

    except Exception as e:
        logging.exception("Chat completion request failed: %s", e)
        print("Sorry, I couldn't process that request right now")
        break

    full_response = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            print(delta, end="", flush=True)
            full_response += delta

    message.append({"role": "assistant", "content": full_response})
    print()  # newline

    # Optional: exit condition
    if incoming_message.lower() == "quit":
        break


#  NEXT IS TO CLEAN THE RESPONSE & MAKE THE REQUEST TO BE COMING FROM EMAIL
