import os
from google import genai
from dotenv import load_dotenv

load_dotenv("local/.env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing models...")
for m in client.models.list():
    print(f"Model: {m.name}, Actions: {m.supported_actions}")
