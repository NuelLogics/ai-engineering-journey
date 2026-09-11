# AI Customer Support Triage & Response System

## Sckye Hospital AI Support Assistant

A Telegram-based AI customer support prototype that classifies incoming messages by intent, detects potential emergencies, and routes non-emergency requests to an AI support agent.

This project was built as part of my **AI Engineering journey**, with a focus on learning how to connect an LLM to a real external application through APIs, structured outputs, webhooks, and deterministic application logic.

---

## Disclaimer

This project is an **educational and experimental AI demo** built for learning purposes.

The hospital information used in this project was obtained from publicly available online sources and is used only to simulate a realistic healthcare support scenario.

This project is **not affiliated with, endorsed by, or associated with Sckye Hospital or its management**.

This project is **not intended for production deployment, real-world customer support, medical diagnosis, or medical advice**.

The emergency response is also only a demonstration of application routing and should not be relied upon for real medical emergencies.

---

## Project Goal

Build a chat-based AI support system that can:

1. Receive messages from a user through Telegram.
2. Determine the user's intent using an LLM.
3. Detect whether the message represents an immediate emergency.
4. Route emergency requests to a deterministic emergency handler.
5. Send non-emergency requests to an AI customer support agent.
6. Return the response to the user through Telegram.

The main goal was not simply to make an LLM respond to a message, but to explore how an AI system can combine **LLM reasoning with deterministic application logic**.

---

## System Architecture

```text
                    ┌──────────────┐
                    │    Telegram  │
                    │     User     │
                    └──────┬───────┘
                           │
                           │ Message
                           ▼
                    ┌──────────────┐
                    │    ngrok     │
                    │ HTTPS Tunnel │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Flask     │
                    │   /webhook   │
                    └──────┬───────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │    Intent Detector  │
                 │                     │
                 │  Pydantic schema +  │
                 │       LLM           │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
          Emergency = True       Emergency = False
                 │                     │
                 ▼                     ▼
        ┌────────────────┐    ┌────────────────┐
        │ Emergency      │    │ Support Agent  │
        │ Handler        │    │                │
        └───────┬────────┘    └───────┬────────┘
                │                     │
                └──────────┬──────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Telegram API │
                    └──────┬───────┘
                           │
                           ▼
                    Telegram User
```

---

## How Intent Detection Works

The system uses an LLM to classify each incoming message into one of five intents:

* `emergency`
* `appointment`
* `billing`
* `medical_inquiry`
* `general_inquiry`

The LLM is required to return a structured JSON response.

Example:

```json
{
  "emergency": false,
  "user_intent": "general_inquiry"
}
```

The response is then validated using **Pydantic**.

The `IntentResult` model uses:

* `BaseModel` for structured data
* `Literal` to restrict valid intent values
* `ConfigDict(extra="forbid")` to reject unexpected fields
* `model_validate_json()` to parse and validate the model response

This prevents the application from blindly trusting arbitrary text returned by the LLM.

---

## Emergency vs Non-Emergency Routing

After the intent is detected, the application uses normal Python logic to determine what happens next.

### Emergency

If:

```text
emergency = true
```

the application does **not** ask the LLM to generate the emergency response.

Instead, it uses a deterministic emergency handler and returns the configured emergency contact information.

### Non-Emergency

For other messages, the request is passed to the support agent.

The support agent uses the hospital context supplied in `data.py` and is instructed not to invent information or provide medical diagnoses.

---

## Technologies Used

* **Python**
* **Flask** — HTTP server and Telegram webhook endpoint
* **Telegram Bot API** — user messaging interface
* **ngrok** — HTTPS tunnel for local webhook development
* **Groq** — LLM API provider
* **OpenAI Python SDK** — OpenAI-compatible client used to communicate with Groq
* **Pydantic** — structured output parsing and validation
* **Requests** — HTTP requests to the Telegram API
* **python-dotenv** — environment variable management
* **Logging** — application and error logging

### Model

The project currently uses:

```text
openai/gpt-oss-120b
```

through Groq's OpenAI-compatible API.

---

## Project Structure

```text
ai-customer-support-triage-and-response-system/
│
├── main.py
├── data.py
├── README.md
└── app.log
```

### `main.py`

Contains the application logic, including:

* Flask application
* Groq/OpenAI-compatible client
* Pydantic intent schema
* Intent detection
* Support agent
* Emergency handler
* Telegram message sending
* Telegram webhook endpoint
* Logging

### `data.py`

Contains the hospital context and system prompts used by the AI components.

### `app.log`

Contains application logs and exception information generated during execution.

---

# Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/martin-adinoyi/ai-engineering-journey.git
```

Navigate to the project:

```bash
cd ai-engineering-journey/ai-customer-support-triage-and-response-system
```

---

## 2. Create and activate a virtual environment

Using Python:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

Install the required packages:

```bash
pip install flask requests python-dotenv openai pydantic
```

---

## 4. Configure environment variables

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

Do **not** commit your `.env` file or API keys to GitHub.

---

# Running the Application Locally

Start the Flask application:

```bash
python main.py
```

The application runs locally on:

```text
http://127.0.0.1:5000
```

The root endpoint can be used as a basic health check:

```text
http://127.0.0.1:5000/
```

Expected response:

```json
{
  "status": "ok",
  "message": "Hospital bot is running!"
}
```

---

# Telegram Webhook Development

Telegram needs a publicly accessible HTTPS endpoint to send webhook requests.

Because this project runs locally during development, **ngrok** is used to expose the Flask application to the internet.

## 1. Start Flask

Keep this terminal running:

```bash
python main.py
```

## 2. Start ngrok

Open another terminal:

```bash
ngrok http 5000
```

ngrok will provide an HTTPS forwarding URL similar to:

```text
https://example.ngrok-free.app
```

Your Telegram webhook URL will be:

```text
https://example.ngrok-free.app/webhook
```

## 3. Configure the Telegram webhook

Set the webhook using Telegram's Bot API:

```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://example.ngrok-free.app/webhook
```

Replace:

```text
<YOUR_BOT_TOKEN>
```

with your Telegram bot token and replace the ngrok URL with the URL generated by your current ngrok session.

## Important

With a normal temporary ngrok URL, the public URL can change when ngrok is restarted.

When the URL changes:

1. Start Flask.
2. Start ngrok.
3. Copy the new HTTPS URL.
4. Update the Telegram webhook to use the new URL.
5. Test the bot again.

---

# Request Flow

When a user sends a message:

```text
Telegram
   ↓
Telegram webhook
   ↓
ngrok
   ↓
Flask /webhook
   ↓
Extract chat ID + message
   ↓
LLM intent detection
   ↓
Pydantic validation
   ↓
Emergency?
   ├── Yes → Emergency handler
   │
   └── No  → Support agent
                    ↓
              Telegram API
                    ↓
                  User
```

---

# Error Handling and Logging

The application uses Python's `logging` module instead of relying entirely on `print()` statements.

Errors from major operations are captured with exception logging, including:

* LLM requests
* Intent detection
* Telegram API requests
* Client initialization

The application writes logs to:

```text
app.log
```

This makes it possible to inspect what happened in the background when something goes wrong.

---

# What I Learned

This project helped me move from simply making an LLM API call to thinking about the structure of an AI system.

Key concepts practiced:

### Structured outputs

I learned that getting JSON from an LLM is not the same as validating that JSON.

The project uses:

```text
LLM
 ↓
JSON
 ↓
Pydantic validation
 ↓
Application logic
```

### Deterministic logic + LLMs

The LLM is used where language understanding is useful, while normal Python logic handles predictable decisions.

For example:

```text
LLM → classify intent
Python → decide which handler runs
```

This is more predictable than allowing the LLM to control the entire application.

### Webhooks

I learned how an external service such as Telegram can communicate with my application through an HTTP webhook.

### API integration

The project connects several independent systems:

```text
Telegram API
      ↕
   Flask
      ↕
    Groq
```

### Error handling

I practiced using:

* `try/except`
* `raise`
* `logging.exception()`
* HTTP response validation with `raise_for_status()`

### Pydantic

I practiced:

* `BaseModel`
* `Literal`
* `ConfigDict(extra="forbid")`
* `model_json_schema()`
* `model_validate_json()`

---

# Current Limitations

This is still a learning project and has several limitations.

* Conversation history is not persisted between messages.
* User sessions are not stored in a database.
* The emergency handler is a simple deterministic demonstration.
* The application currently runs locally during development.
* ngrok is being used as a temporary development tunnel.
* There is no authentication or production webhook security layer.
* There are no automated tests yet.
* The application is not designed for real medical use.
* The current architecture has not been production-hardened.

---

# Possible Future Improvements

Potential improvements include:

* Persistent conversation history
* Database-backed user sessions
* More specialized intent handlers
* Automated tests
* Better webhook security
* Production deployment
* FastAPI migration/implementation
* More robust observability
* Rate limiting
* Background task processing
* Human handoff for complex requests

These improvements are intentionally outside the scope of this first version.

---

## Project Status

**Completed — AI Engineering learning project**

The current version successfully demonstrates:

* LLM-based intent classification
* Structured LLM output
* Pydantic validation
* Deterministic routing
* Flask HTTP endpoints
* Telegram webhook integration
* Telegram API responses
* ngrok local development tunneling
* Error handling and logging

The project was built as part of my progression from **Python foundations toward AI system design and AI engineering**.
