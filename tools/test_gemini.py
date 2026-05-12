import os
from google import genai
from dotenv import load_dotenv

load_dotenv("local/.env")
api_key = os.getenv("GEMINI_API_KEY")
print(f"Using API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

client = genai.Client(api_key=api_key)
print("Calling Gemini API...")
try:
    response = client.models.generate_content(model="gemini-1.5-flash", contents="Hello")
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
