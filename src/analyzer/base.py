import os
import json
from dotenv import load_dotenv
from .providers.factory import LLMFactory

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

class BaseAnalyzer:
    def __init__(self):
        self.provider = LLMFactory.create_provider()
        self.model_name = self.provider.get_model_name()

    def _get_active_persona(self):
        # 設定ファイルから現在のキャラクターを取得
        local_dir = os.getenv("KAKEIBO_LOCAL_DIR", "local")
        settings_path = os.path.join(local_dir, "config/settings.json")
        persona = 'gal' # デフォルト
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    persona = settings.get("ai", {}).get("active_persona", persona)
            except Exception as e:
                print(f"Warning: Failed to load settings.json, using default persona: {e}")
        return persona

    def _load_prompt_file(self, file_path: str) -> str:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _get_persona_settings(self):
        active_persona = self._get_active_persona()
        persona_path = f"prompts/personas/{active_persona}.md"
        if not os.path.exists(persona_path):
            persona_path = "prompts/personas/default.md"
        return self._load_prompt_file(persona_path)
