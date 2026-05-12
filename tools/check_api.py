import requests
import json

try:
    print("Requesting simulation...")
    res = requests.get("http://localhost:8000/api/life-plan/simulation")
    data = res.json()
    advice = data.get("advice", "")
    print(f"Advice (first 100 chars): {advice[:100]}")
    if "エラーが発生した" in advice:
        print("FAILED: Response still contains error message")
    else:
        print("SUCCESS: AI advice generated successfully!")
except Exception as e:
    print(f"Error checking API: {e}")
