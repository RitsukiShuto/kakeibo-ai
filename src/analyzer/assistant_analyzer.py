import json
from typing import List, Optional
from src.models import Transaction
from .base import BaseAnalyzer

class AssistantAnalyzer(BaseAnalyzer):
    def parse_reimbursement_text(self, text: str, total_amount: int) -> Optional[dict]:
        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。ユーザーが入力した立替や割り勘に関する説明を解析し、"
            "「ユーザー自身の自己負担額」を算出してください。\n"
            "入力には、総額、人数、あるいは特定の金額が含まれる場合があります。\n"
            "返却は以下のJSON形式のみで行ってください。\n"
            "{\"self_amount\": 整数, \"reason\": \"算出した理由の短い説明\"}"
        )
        user_input = f"総額: {total_amount}円\n説明: {text}"
        try:
            raw_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_input,
                response_mime_type="application/json",
                temperature=0.1
            )
            result = json.loads(raw_text.strip())
            return result
        except Exception as e:
            print(f"Error parsing reimbursement text: {e}")
            return None

    def detect_potential_reimbursements(self, transactions: List[Transaction]) -> List[dict]:
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
            raw_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=f"対象明細:\n{tx_list_text}",
                response_mime_type="application/json",
                temperature=0.1
            )
            result = json.loads(raw_text.strip())
            return result.get("suggestions", [])
        except Exception as e:
            print(f"Error detecting reimbursements: {e}")
            return []

    def suggest_category_mappings(self, unmapped_items: List[dict], target_categories: List[str]) -> List[dict]:
        if not unmapped_items or not target_categories:
            return []
        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。金融サービスから取得した「元のカテゴリ・中項目」を、"
            "ユーザーが設定した「予算カテゴリ」のどれに分類すべきか提案してください。\n"
            "可能な限り正確に分類し、判断がつかない場合は最も近いものを選んでください。\n"
            "返却は以下のJSON形式のみで行ってください。コードブロックは含めないでください。\n"
            "{\"suggestions\": [{\"raw_category\": \"元の大項目\", \"raw_genre\": \"元の中項目\", \"suggested_category\": \"予算カテゴリ名\", \"suggested_genre\": \"提案する中項目名\", \"reason\": \"理由\"}]}"
        )
        user_input = {
            "unmapped_items": unmapped_items,
            "target_categories": target_categories
        }
        try:
            raw_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=f"対象データ:\n{json.dumps(user_input, ensure_ascii=False)}",
                response_mime_type="application/json",
                temperature=0.1
            )
            result = json.loads(raw_text.strip())
            return result.get("suggestions", [])
        except Exception as e:
            print(f"Error suggesting category mappings: {e}")
            return []
