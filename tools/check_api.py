import requests
import json

BASE_URL = "http://localhost:8000"

def check_simulation():
    try:
        print("Requesting simulation...")
        res = requests.get(f"{BASE_URL}/api/life-plan/simulation")
        res.raise_for_status()
        data = res.json()
        trajectory = data.get("trajectory", [])
        print(f"SUCCESS: Simulation trajectory generated with {len(trajectory)} data points.")
        return data
    except Exception as e:
        print(f"FAILED: Simulation check failed: {e}")
        return None

def check_advice():
    try:
        print("Requesting AI advice (this may take a few seconds)...")
        res = requests.get(f"{BASE_URL}/api/life-plan/advice")
        res.raise_for_status()
        data = res.json()
        advice = data.get("advice", "")
        print(f"Advice (first 100 chars): {advice[:100]}...")
        if "エラー" in advice or not advice:
            print("FAILED: Advice generation returned error or empty content.")
        else:
            print("SUCCESS: AI advice generated successfully!")
        return data
    except Exception as e:
        print(f"FAILED: Advice check failed: {e}")
        return None

if __name__ == "__main__":
    print("--- Kakeibo AI Life Plan API Check ---")
    sim_data = check_simulation()
    if sim_data:
        check_advice()
