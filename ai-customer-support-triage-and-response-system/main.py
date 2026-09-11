import os
import logging
from flask import Flask, request, jsonify
import requests
from pydantic import BaseModel, ConfigDict
from openai import OpenAI
from dotenv import load_dotenv
from data import system_prompt, SUPPORT_SYSTEM_PROMPT
from typing import Literal


load_dotenv()
# Initialize Flask app
app = Flask(__name__)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
)
# Telegram Configurations
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
# https://api.telegram.org/bot<token>/sendMessage?chat_id=<chat_id>&text=Hello   *


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


# conversation = []


def send_telegram_message(chat_id: int, text: str):
    """Utility function to fire HTTP POST requests back to Telegram API"""
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(TELEGRAM_API_URL, json=payload)
    except Exception:
        logging.exception("Failed to send message to Telegram")


# ----------------------------------------------------------------
# REPLACING THE WHILE LOOP WITH TELEGRAM WEBHOOK TRIGGER
# ----------------------------------------------------------------
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json()

    # Ensure the update actually contains a text message
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        incoming_message = update["message"]["text"]

        # NOTE: For multiple users, you'd usually pull/save this conversation history
        # from a database (like SQLite/Redis) matching the chat_id.
        # For now, we seed an isolated session list for this single request block.
        current_conversation = [{"role": "user", "content": incoming_message}]

        try:
            result = detect_intent(client, user_question=incoming_message)
        except Exception as error:
            logging.exception("Intent detection failed")
            send_telegram_message(
                chat_id, "Sorry, something went wrong. Please try again."
            )
            return jsonify({"status": "error"}), 200

        if result.emergency:
            emergency_msg = (
                "⚠️ This may be an emergency. Please contact the hospital immediately.\n"
                f"Emergency contact: {emergency_tool()}"
            )
            send_telegram_message(chat_id, emergency_msg)
        else:
            try:
                answer = support_agent(client, current_conversation)
                send_telegram_message(chat_id, answer)
            except Exception as error:
                send_telegram_message(
                    chat_id, "Sorry, something went wrong. Please try again."
                )

    # Always return a 200 OK so Telegram doesn't keep retrying the same message
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# while True:
#     incoming_message = input("You: ")
#     if incoming_message.lower() == "quit":
#         break
#     conversation.append({"role": "user", "content": incoming_message})

#     try:
#         result = detect_intent(client, user_question=incoming_message)
#     except Exception as error:
#         logging.exception("Intent detection failed")
#         print(f"Technical error: {error}")
#         print("Sorry, something went wrong. Please try again.")
#         continue

#     # print(result.user_intent)

#     if result.emergency:
#         print("This may be an emergency. Please contact the hospital immediately.")
#         print(f"Emergency contact: {emergency_tool()}")
#         # emergency handler will go here
#     else:
#         try:
#             answer = support_agent(client, conversation)
#             print(f"Assistant: {answer}")
#             conversation.append({"role": "assistant", "content": answer})
#         except Exception as error:
#             print(f"Technical error: {error}")
#             print("Sorry, something went wrong. Please try again.")
