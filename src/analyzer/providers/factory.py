import os
import json
from .base import BaseLLMProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider

class LLMFactory:
    @staticmethod
    def create_provider() -> BaseLLMProvider:
        provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
        
        # モデル名の取得 (設定ファイル優先)
        settings_path = "local/config/settings.json"
        model_name = None
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    model_name = settings.get("ai", {}).get("active_model")
            except Exception as e:
                # ログに出力
                print(f"Error: Failed to parse settings.json: {e}")

        # 設定がない場合はエラーを投げる (ハードコードされたフォールバックを廃止)
        if not model_name:
            error_msg = f"AI model is not configured. Please check 'active_model' in {settings_path}."
            print(f"Error: {error_msg}")
            raise ValueError(error_msg)

        if provider_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is missing.")
            return GeminiProvider(api_key=api_key, model_name=model_name)
        
        elif provider_type == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
            return OllamaProvider(base_url=base_url, model_name=model_name)
        
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider_type}")
