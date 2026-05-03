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

        # JSONスキーマの明示
        json_schema = {
            "slack_summary": "Slack通知用の150文字程度の要約文（ギャル風）",
            "obsidian_report": "Obsidian用のMarkdown形式の詳細レポート全文",
            "actions": [
                {"command": "Now/Keep/Stopなどの短いコマンド", "description": "具体的なアクション内容"}
            ],
            "asset_breakdown": [
                {"category": "資産カテゴリ名", "amount": 10000}
            ],
            "totonoi_score": "0-100の整数",
            "savings_potential": "今月あといくら節約できるかの概算額（整数）"
        }

        full_prompt = (
            f"{system_prompt}\n\n"
            f"## 今回の分析の特別指示 ({timeframe})\n{timeframe_prompt}\n\n"
            f"## 分析対象データ\n{user_input}\n\n"
            f"## 出力形式\n"
            f"以下のJSONスキーマに従って、純粋なJSONオブジェクトのみを出力してください。\n"
            f"Markdownのコードブロック（```json）は含めないでください。\n"
            f"全ての項目を必ず埋めてください。\n\n"
            f"JSON Schema:\n{json.dumps(json_schema, ensure_ascii=False, indent=2)}"
        )

        print(f"AI analyzing {len(data)} transactions and {len(assets_summary)} asset categories...")
        
        try:
            response = self.model.generate_content(full_prompt)
            raw_text = response.text.strip()
            
            # JSONの抽出ロジックを強化
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_candidate = raw_text[start_idx:end_idx+1]
            else:
                json_candidate = raw_text

            # 制御文字などの除去
            json_candidate = json_candidate.replace('\n', ' ').replace('\r', '')
            # 連続するスペースを1つに（パースエラー軽減）
            import re
            json_candidate = re.sub(r'\s+', ' ', json_candidate)

            result_json = json.loads(json_candidate)
            ai_response = AIResponse(**result_json)
            return ai_response

        except Exception as e:
            print(f"AI Analysis error: {e}")
            try:
                # 文字化け対策としてエンコードを考慮して出力
                print(f"Raw text (first 500 chars): {raw_text[:500].encode('utf-8', errors='replace').decode('utf-8')}")
            except:
                print("Could not display raw text due to encoding issues.")
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
