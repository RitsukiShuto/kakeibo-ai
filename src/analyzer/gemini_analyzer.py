import os
import json
import google.generativeai as genai
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from src.models import Transaction, Asset, AIResponse

load_dotenv()

class GeminiAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        
        genai.configure(api_key=api_key)
        self.model = self._select_best_model()

    def _select_best_model(self):
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # 未来のモデル (2.0, 2.5) を優先
            priority_keywords = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
            for keyword in priority_keywords:
                for model_name in available_models:
                    if keyword in model_name:
                        print(f"Selected model: {model_name}")
                        return genai.GenerativeModel(
                            model_name,
                            generation_config={"response_mime_type": "application/json"}
                        )
            return genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})
        except Exception:
            return genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})

    def analyze_kakeibo(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, profile: dict, previous_summary: Optional[str] = None) -> Optional[AIResponse]:
        # ... (プロンプト組み立て部分は変更なし)
        system_prompt_template = self._load_prompt_file("prompts/system_prompt.md")
        timeframe_prompt = self._load_prompt_file(f"prompts/{timeframe}_prompt.md")
        
        user_info = profile.get("user", {})
        target = user_info.get("target", {})
        system_prompt = system_prompt_template.format(
            name=user_info.get('name', 'せんぱい'),
            occupation=user_info.get('occupation', '不明'),
            hobbies=', '.join(user_info.get('hobbies', [])),
            investment_policy=user_info.get('investment_policy', '未設定'),
            target_date=target.get('date', '未設定'),
            target_description=target.get('description', '目標なし')
        )

        user_input = self._create_user_input_text(data, assets_summary, timeframe, previous_summary)

        full_prompt = f"{system_prompt}\n\n## 今回の分析の特別指示 ({timeframe})\n{timeframe_prompt}\n\n## 分析対象データ\n{user_input}\n\nJSON形式で出力してください。Markdownのコードブロックなどは含めず、純粋なJSONのみを返してください。データが少ない場合や無い場合でも、現状を肯定的に分析して必ず全てのキーを含むJSONを生成してください。"

        print(f"AI analyzing {len(data)} transactions and {len(assets_summary)} asset categories...")
        
        try:
            response = self.model.generate_content(full_prompt)
            raw_text = response.text.strip()
            
            # Markdownのコードブロック（```json ... ```）を除去するロジック
            if raw_text.startswith("```"):
                # 最初と最後の ``` 行を削除
                lines = raw_text.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines[-1].startswith("```"): lines = lines[:-1]
                raw_text = "\n".join(lines).strip()
            
            # 余分なテキストが混じっている場合、最初の { と最後の } を探す
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                raw_text = raw_text[start_idx:end_idx+1]

            result_json = json.loads(raw_text)
            ai_response = AIResponse(**result_json)
            return ai_response

        except Exception as e:
            print(f"AI Analysis error: {e}")
            print(f"Raw text was: {response.text if 'response' in locals() else 'N/A'}")
            return None

    def _load_prompt_file(self, file_path: str) -> str:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _get_system_prompt(self, profile: dict) -> str:
        # このメソッドは analyze_kakeibo 内に統合されたため不要になりましたが
        # 互換性のために残すか削除します。今回はシンプルにするため削除扱いとします。
        pass

    def _create_user_input_text(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, previous_summary: Optional[str]) -> str:
        text = f"### 分析期間: {timeframe}\n\n"
        
        if previous_summary:
            text += f"#### 0. 前回の分析サマリー\n{previous_summary}\n\n"

        text += "#### 1. 今回追加された差分明細\n"
        if not data:
            text += "なし\n"
        for t in data:
            text += f"- {t.transaction_date}: {t.category}({t.genre}) {t.amount}円 {t.comment} [{t.source}]\n"
            
        text += "\n#### 2. 現在の資産状況（カテゴリ別集計済み）\n"
        total_asset = 0
        for a in assets_summary:
            text += f"- {a['category']}: {a['amount']:,}円\n"
            total_asset += a['amount']
        text += f"**資産総額: {total_asset:,}円**\n"
        
        return text
