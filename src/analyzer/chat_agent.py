from typing import List
from src.models import Transaction
from .base import BaseAnalyzer

class ChatAgent(BaseAnalyzer):
    def chat(self, message: str, history: List[dict] = None, profile: dict = None, budget: dict = None, assets_summary: List[dict] = None, recent_transactions: List[Transaction] = None, model_override: str = None) -> str:
        persona_settings = self._get_persona_settings()
        
        system_prompt = (
            f"{persona_settings}\n\n"
            "あなたは優秀な家計簿アシスタントです。ユーザーからの質問に対して、"
            "現在の家計状況を考慮した具体的で親しみやすいアドバイスを提供してください。\n"
        )
        
        if assets_summary:
            total = sum(a['amount'] for a in assets_summary)
            system_prompt += f"\n現在の総資産: {total:,}円\n"
            system_prompt += "資産内訳:\n" + "\n".join([f"- {a['category']}: {a['amount']:,}円" for a in assets_summary])
            
        if recent_transactions:
            system_prompt += "\n\n最近の支出明細（直近10件）:\n"
            for t in recent_transactions[:10]:
                system_prompt += f"- {t.transaction_date}: {t.category}({t.genre}) {t.amount}円 {t.comment}\n"

        original_model = None
        if model_override:
            original_model = self.provider.model_name
            self.provider.model_name = model_override

        try:
            result = self.provider.chat(
                system_prompt=system_prompt,
                history=history or [],
                message=message,
                temperature=0.7
            )
            if original_model:
                self.provider.model_name = original_model
            return result
        except Exception as e:
            if original_model:
                self.provider.model_name = original_model
            print(f"Chat error: {e}")
            return "ごめん、ちょっと調子が悪いみたい。後でもう一度話しかけてね！"
