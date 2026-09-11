import os
import logging
from typing import Literal

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI
from pydantic import BaseModel, ConfigDict

from data import SUPPORT_SYSTEM_PROMPT, system_prompt


load_dotenv()

app = Flask(__name__)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    if TELEGRAM_BOT_TOKEN
    else None
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
    return "+234 810 636 6523"


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


def send_telegram_message(chat_id: int, text: str):
    """Utility function to fire HTTP POST requests back to Telegram API"""

    if not TELEGRAM_API_URL:
        logging.error("TELEGRAM_BOT_TOKEN missing. Cannot send message.")
        return

    payload = {"chat_id": chat_id, "text": text}

    try:
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("Telegram message sent successfully")

    except Exception:
        logging.exception("Failed to send message to Telegram")


@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "Hospital bot is running!"}), 200


# ----------------------------------------------------------------
# REPLACING THE WHILE LOOP WITH TELEGRAM WEBHOOK TRIGGER
# ----------------------------------------------------------------
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    if not request.is_json:
        logging.error("Received non-JSON request")
        return jsonify({"status": "error", "message": "Invalid request format"}), 400
    update = request.get_json(silent=True)

    if not update:
        return jsonify({"status": "empty_update"}), 400

    # Ensure the update contains a message with text before processing
    if not update:
        return jsonify({"status": "empty_update"}), 400

    message = update.get("message")
    if not message or "text" not in message:
        return jsonify({"status": "ignored"}), 200

    chat_id = update["message"]["chat"]["id"]
    incoming_message = update["message"]["text"]

    # NOTE: For multiple users, you'd usually pull/save this conversation history
    # from a database (like SQLite/Redis) matching the chat_id.
    # For now, we seed an isolated session list for this single request block.
    current_conversation = [{"role": "user", "content": incoming_message}]

    try:
        result = detect_intent(client, user_question=incoming_message)
    except Exception:
        logging.exception("Intent detection failed")
        send_telegram_message(chat_id, "Sorry, something went wrong. Please try again.")
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
        except Exception:
            send_telegram_message(
                chat_id, "Sorry, something went wrong. Please try again."
            )

    # Always return a 200 OK so Telegram doesn't keep retrying the same message
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
