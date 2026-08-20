import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.0-flash")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chat ended.")
        break

    try:
        response = model.generate_content(user_input)
        print("Gemini:", response.text)
    except Exception as e:
        print("API error:", e)
