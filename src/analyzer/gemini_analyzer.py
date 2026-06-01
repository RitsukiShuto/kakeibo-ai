import os
from typing import List, Optional
from src.models import Transaction, AIResponse
from .review_analyzer import ReviewAnalyzer
from .assistant_analyzer import AssistantAnalyzer
from .life_plan_analyzer import LifePlanAnalyzer
from .chat_agent import ChatAgent

class KakeiboAnalyzer:
    def __init__(self):
        self.review_analyzer = ReviewAnalyzer()
        self.assistant_analyzer = AssistantAnalyzer()
        self.life_plan_analyzer = LifePlanAnalyzer()
        self.chat_agent = ChatAgent()
        # provider attributes are used by some consumers
        self.provider = self.review_analyzer.provider
        self.model_name = self.review_analyzer.model_name

    def analyze_kakeibo(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, profile: dict, budget: dict = None, previous_summary: Optional[str] = None, actual_monthly_income: int = 0, comparison_data: dict = None, pending_reimbursements: List[Transaction] = None) -> Optional[AIResponse]:
        return self.review_analyzer.analyze_kakeibo(
            data, assets_summary, timeframe, profile, budget, 
            previous_summary, actual_monthly_income, 
            comparison_data, pending_reimbursements
        )

    def parse_reimbursement_text(self, text: str, total_amount: int) -> Optional[dict]:
        return self.assistant_analyzer.parse_reimbursement_text(text, total_amount)

    def detect_potential_reimbursements(self, transactions: List[Transaction]) -> List[dict]:
        return self.assistant_analyzer.detect_potential_reimbursements(transactions)

    def suggest_category_mappings(self, unmapped_items: List[dict], target_categories: List[str]) -> List[dict]:
        return self.assistant_analyzer.suggest_category_mappings(unmapped_items, target_categories)

    def analyze_life_plan(self, trajectory: List[dict], profile: dict, budget: dict) -> str:
        return self.life_plan_analyzer.analyze_life_plan(trajectory, profile, budget)

    def chat(self, message: str, history: List[dict] = None, profile: dict = None, budget: dict = None, assets_summary: List[dict] = None, recent_transactions: List[Transaction] = None, model_override: str = None) -> str:
        return self.chat_agent.chat(
            message, history, profile, budget, 
            assets_summary, recent_transactions, model_override
        )

class GeminiAnalyzer(KakeiboAnalyzer):
    """
    Backward compatibility class name.
    """
    pass
