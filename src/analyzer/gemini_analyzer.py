import os
import json
from google import genai
from google.genai import types
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from src.models import Transaction, Asset, AIResponse

load_dotenv("local/.env")

class GeminiAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = self._select_best_model()

    def _select_best_model(self):
        # より高度で正確な推論・着地予測を行うため、最強クラスのProモデルを採用
        model = 'gemini-2.0-pro-exp'
        print(f"Selected model: {model}")
        return model

    def analyze_kakeibo(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, profile: dict, budget: dict = None, previous_summary: Optional[str] = None) -> Optional[AIResponse]:
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

        user_input = self._create_user_input_text(data, assets_summary, timeframe, budget, previous_summary)

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
            "budget_status": [
                {"category": "食費", "budget": 40000, "actual": 42000, "status": "超過"}
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
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

    def _create_user_input_text(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, budget: dict = None, previous_summary: Optional[str] = None) -> str:
        text = f"### 分析期間: {timeframe}\n\n"
        
        if previous_summary:
            text += f"#### 0. 前回の分析サマリー\n{previous_summary}\n\n"

        if budget:
            text += "#### 1. 設定されている予算 (月次)\n"
            monthly_budget = budget.get("monthly", {})
            text += f"- 月間総収入目標: {monthly_budget.get('income', 0):,}円\n"
            text += f"- 貯蓄目標: {monthly_budget.get('savings_goal', 0):,}円\n"
            text += f"- 投資目標: {monthly_budget.get('investment_goal', 0):,}円\n"
            text += "  - カテゴリ別予算:\n"
            for cat, amt in monthly_budget.get("categories", {}).items():
                text += f"    - {cat}: {amt:,}円\n"
            text += "\n"

        text += "#### 2. 今回追加された差分明細\n"
        if not data:
            text += "なし\n"
        for t in data:
            text += f"- {t.transaction_date}: {t.category}({t.genre}) {t.amount}円 {t.comment} [{t.source}]\n"
            
        text += "\n#### 3. 現在の資産状況（カテゴリ別集計済み）\n"
        total_asset = 0
        for a in assets_summary:
            text += f"- {a['category']}: {a['amount']:,}円\n"
            total_asset += a['amount']
        text += f"**資産総額: {total_asset:,}円**\n"
        
        return text
