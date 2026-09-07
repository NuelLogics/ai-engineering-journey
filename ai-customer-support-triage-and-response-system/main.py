import os
import logging
from pydantic import BaseModel, ConfigDict
from openai import OpenAI
from dotenv import load_dotenv
from data import system_prompt, SUPPORT_SYSTEM_PROMPT
from typing import Literal


load_dotenv()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
)


def create_client():
    try:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from the .env file")

        return OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    except Exception:
        logging.exception("Error initializing OpenAI client")
        raise


client = create_client()

conversation = [{"role": "system", "content": system_prompt}]


class IntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    emergency: bool
    user_intent: Literal[
        "emergency",
        "appointment",
        "billing",
        "medical_inquiry",
        "general_inquiry",
    ]


def detect_intent(client, user_question: str) -> IntentResult:

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question},
    ]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0,
            max_completion_tokens=1000,
            # stream=True,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "IntentResult",
                    "strict": True,
                    "schema": IntentResult.model_json_schema(),
                },
            },
        )

    except Exception:
        logging.exception("Chat completion request failed")
        raise

    raw_response = response.choices[0].message.content
    return IntentResult.model_validate_json(raw_response)


def emergency_tool():
    emergency_number = "+234 810 636 6523"
    return emergency_number


# if intent.user_intent.lower() == "emergency":
#     emergency_tool()


def support_agent(client, conversation: list[dict[str, str]]) -> str:

    messages = [
        {"role": "system", "content": SUPPORT_SYSTEM_PROMPT},
        *conversation,
    ]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.1,
            max_completion_tokens=1000,
        )
        return response.choices[0].message.content

    except Exception:
        logging.exception("Chat completion request failed")
        raise


conversation = []

while True:
    incoming_message = input("You: ")
    if incoming_message.lower() == "quit":
        break
    conversation.append({"role": "user", "content": incoming_message})

    try:
        result = detect_intent(client, user_question=incoming_message)
    except Exception as error:
        logging.exception("Intent detection failed")
        print(f"Technical error: {error}")
        print("Sorry, something went wrong. Please try again.")
        continue

    print(result.user_intent)

    if result.emergency:
        print("This may be an emergency. Please contact the hospital immediately.")
        print(f"Emergency contact: {emergency_tool()}")
        # emergency handler will go here
    else:
        try:
            answer = support_agent(client, conversation)
            print(f"Assistant: {answer}")
            conversation.append({"role": "assistant", "content": answer})
        except Exception as error:
            print(f"Technical error: {error}")
            print("Sorry, something went wrong. Please try again.")
