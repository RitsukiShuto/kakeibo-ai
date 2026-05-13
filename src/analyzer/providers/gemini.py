import os
from google import genai
from google.genai import types
from typing import List, Dict, Any
from .base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
    def _normalize_model_name(self, model_name: str) -> str:
        """
        モデル名に必要なプレフィックスを付与する。
        ハードコードされたマッピングを排除し、設定ファイルのIDを尊重する。
        """
        if not model_name.startswith("models/"):
            return f"models/{model_name}"
        return model_name

    def generate_content(self, system_prompt: str, user_prompt: str, response_mime_type: str = "text/plain", temperature: float = 0.7) -> str:
        model = self._normalize_model_name(self.model_name)
        # Gemini SDK supports system_instruction in some versions, but here we combine or use config
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self.client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type=response_mime_type,
                temperature=temperature
            )
        )
        return response.text.strip()

    def chat(self, system_prompt: str, history: List[Dict[str, str]], message: str, temperature: float = 0.7) -> str:
        model = self._normalize_model_name(self.model_name)
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        
        contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
        
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature
            )
        )
        return response.text.strip()

    def get_model_name(self) -> str:
        return self.model_name
