import os
import json
import re
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
        # 設定ファイルからモデルを取得
        settings_path = "local/config/settings.json"
        model = 'gemini-2.0-flash' # デフォルト
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    model = settings.get("ai", {}).get("active_model", model)
            except Exception as e:
                print(f"Warning: Failed to load settings.json, using default model: {e}")
                
        print(f"Selected model: {model}")
        return model

    def analyze_kakeibo(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, profile: dict, budget: dict = None, previous_summary: Optional[str] = None, actual_monthly_income: int = 0, comparison_data: dict = None, pending_reimbursements: List[Transaction] = None) -> Optional[AIResponse]:
        persona_settings = self._load_prompt_file("prompts/persona_settings.md")
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

        user_input = self._create_user_input_text(data, assets_summary, timeframe, budget, previous_summary, actual_monthly_income, comparison_data, pending_reimbursements)

        json_schema = {
            "slack_report": "Slack用の詳細レポート本文（Markdown/絵文字を駆使して、ギャル風に。※あとの'actions'セクションと重複するため、具体的なアクションリストはここには含めないでください）",
            "obsidian_report": "Obsidian用のMarkdown形式の詳細レポート全文（Calloutやアクションリストも含めて、1つの完結した記事として作成してください）",
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
            f"{persona_settings}\n\n"
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
            
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_candidate = raw_text[start_idx:end_idx+1]
            else:
                json_candidate = raw_text

            json_candidate = json_candidate.replace('\n', ' ').replace('\r', '')
            json_candidate = re.sub(r'\s+', ' ', json_candidate)

            result_json = json.loads(json_candidate)
            
            # 使用したモデル名とトークン使用量を記録
            usage = response.usage_metadata
            result_json["model_name"] = self.model_name
            result_json["prompt_tokens"] = usage.prompt_token_count
            result_json["response_tokens"] = usage.candidates_token_count
            result_json["total_tokens"] = usage.total_token_count
            
            ai_response = AIResponse(**result_json)
            return ai_response

        except Exception as e:
            print(f"AI Analysis error: {e}")
            try:
                print(f"Raw text (first 500 chars): {raw_text[:500].encode('utf-8', errors='replace').decode('utf-8')}")
            except:
                print("Could not display raw text due to encoding issues.")
            return None

    def parse_reimbursement_text(self, text: str, total_amount: int) -> Optional[dict]:
        """
        立替に関する自然言語入力を解析し、自己負担額を算出する
        """
        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。ユーザーが入力した立替や割り勘に関する説明を解析し、"
            "「ユーザー自身の自己負担額」を算出してください。\n"
            "入力には、総額、人数、あるいは特定の金額が含まれる場合があります。\n"
            "返却は以下のJSON形式のみで行ってください。\n"
            "{\"self_amount\": 整数, \"reason\": \"算出した理由の短い説明\"}"
        )

        user_input = f"総額: {total_amount}円\n説明: {text}"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{system_prompt}\n\n{user_input}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            print(f"Error parsing reimbursement text: {e}")
            return None

    def detect_potential_reimbursements(self, transactions: List[Transaction]) -> List[dict]:
        """
        最近の明細から立替の可能性がある項目をAIで推測する
        """
        if not transactions:
            return []

        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。支払い明細のリストを見て、"
            "「これは実は立替や割り勘なのではないか？」と思われる項目をピックアップしてください。\n"
            "高額な外食、複数人での利用が推測される場所、普段の支出パターンと異なるものなどが候補になります。\n"
            "返却は以下のJSON形式のみで行ってください。\n"
            "{\"suggestions\": [{\"transaction_id\": \"ID\", \"reason\": \"推測理由\", \"confidence\": 0.0-1.0}]}"
        )

        tx_list_text = "\n".join([
            f"- ID: {t.transaction_id}, 日付: {t.transaction_date}, カテゴリ: {t.category}, 金額: {t.amount}円, 内容: {t.comment}"
            for t in transactions
        ])

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{system_prompt}\n\n対象明細:\n{tx_list_text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            result = json.loads(response.text.strip())
            return result.get("suggestions", [])
        except Exception as e:
            print(f"Error detecting reimbursements: {e}")
            return []

    def _load_prompt_file(self, file_path: str) -> str:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _create_user_input_text(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, budget: dict = None, previous_summary: Optional[str] = None, actual_monthly_income: int = 0, comparison_data: dict = None, pending_reimbursements: List[Transaction] = None) -> str:
        text = f"### 分析期間: {timeframe}\n\n"
        
        if previous_summary:
            text += f"#### 0. 前回の分析サマリー\n{previous_summary}\n\n"

        if budget:
            text += "#### 1. 設定されている予算・収入状況 (月次)\n"
            monthly_budget = budget.get("monthly", {})
            budget_income = monthly_budget.get('income', 0)
            
            has_salary_arrived = actual_monthly_income >= (budget_income * 0.8)
            
            text += f"- 月間総収入予算: {budget_income:,}円\n"
            text += f"- 今月の現在までの実績収入: {actual_monthly_income:,}円\n"
            
            if has_salary_arrived:
                text += "👉 **【判定】今月の給料は受取済みです。分析には実績の収入額をベースに使用してください。**\n"
            else:
                text += f"👉 **【判定】今月の給料はまだ入っていないか、全額ではありません。分析には予算額（{budget_income:,}円）を暫定的な収入として参照してください。**\n"

            text += f"- 貯蓄目標: {monthly_budget.get('savings_goal', 0):,}円\n"
            text += f"- 投資目標: {monthly_budget.get('investment_goal', 0):,}円\n"
            text += "  - カテゴリ別予算:\n"
            for cat, amt in monthly_budget.get("categories", {}).items():
                text += f"    - {cat}: {amt:,}円\n"
            text += "\n"

        if comparison_data:
            text += "#### 2. 前期間との定量比較データ\n"
            # 純資産の前月比
            if "prev_total_assets" in comparison_data:
                curr = sum(a['amount'] for a in assets_summary)
                prev = comparison_data["prev_total_assets"]
                diff = curr - prev
                ratio = (diff / prev * 100) if prev != 0 else 0
                text += f"- 純資産の前月比: {diff:+,}円 ({ratio:+.1f}%)\n"
            
            # 収支の改善度合い
            if "prev_balance" in comparison_data:
                curr_income = actual_monthly_income
                # 立替を考慮した支出計算
                curr_expense = sum(
                    (t.self_amount if t.is_reimbursement and t.self_amount is not None else t.amount)
                    for t in data if t.mode == 'payment'
                )
                curr_bal = curr_income - curr_expense
                
                prev_bal = comparison_data["prev_balance"]
                bal_diff = curr_bal - prev_bal
                
                # 改善率の計算 (分母が0または負の場合の考慮が必要だが、簡易的に)
                if prev_bal != 0:
                    bal_ratio = (bal_diff / abs(prev_bal) * 100)
                else:
                    bal_ratio = 0
                
                text += f"- 収支の改善度 (前期間比): {bal_diff:+,}円 ({bal_ratio:+.1f}%)\n"
            text += "\n"

        text += "#### 3. 今回追加された差分明細\n"
        if not data:
            text += "なし\n"
        for t in data:
            mode_ja = "支出" if t.mode == "payment" else "収入" if t.mode == "income" else "振替"
            amount_display = f"{t.amount}円"
            if t.is_reimbursement and t.self_amount is not None:
                amount_display = f"{t.amount}円 (自己負担: {t.self_amount}円, 立替中)"

            text += f"- {t.transaction_date}: [{mode_ja}] {t.category}({t.genre}) {amount_display} {t.comment} [{t.source}]\n"

        if pending_reimbursements:
            text += "\n#### 4. 未精算の立替金リスト (リマインド対象)\n"
            for t in pending_reimbursements:
                reimb_amt = t.amount - (t.self_amount or 0)
                text += f"- {t.transaction_date}: {t.category} {reimb_amt:,}円 (元金額: {t.amount:,}円) {t.comment}\n"

        text += "\n#### 5. 現在の資産状況（カテゴリ別集計済み）\n"
        total_asset = 0
        for a in assets_summary:
            text += f"- {a['category']}: {a['amount']:,}円\n"
            total_asset += a['amount']
        text += f"**資産総額: {total_asset:,}円**\n"

        return text
