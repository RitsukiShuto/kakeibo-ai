import json
import requests
from typing import List, Dict, Any
from .base import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name

    def generate_content(self, system_prompt: str, user_prompt: str, response_mime_type: str = "text/plain", temperature: float = 0.7) -> str:
        url = f"{self.base_url}/api/generate"
        
        # Ollama does not directly support 'application/json' mime type in the same way as Gemini
        # but we can ask in the prompt. If using Ollama's format parameter:
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if response_mime_type == "application/json":
            payload["format"] = "json"

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()

    def chat(self, system_prompt: str, history: List[Dict[str, str]], message: str, temperature: float = 0.7) -> str:
        url = f"{self.base_url}/api/chat"
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "").strip()

    def get_model_name(self) -> str:
        return self.model_name
