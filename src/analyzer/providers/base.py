from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_content(self, system_prompt: str, user_prompt: str, response_mime_type: str = "text/plain", temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    def chat(self, system_prompt: str, history: List[Dict[str, str]], message: str, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
