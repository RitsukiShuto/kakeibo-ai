import os
from unittest.mock import MagicMock, patch
from datetime import date
from src.analyzer.gemini_analyzer import KakeiboAnalyzer
from src.models import Transaction

def test_prompt_content(persona):
    with patch('src.analyzer.providers.factory.LLMFactory.create_provider') as mock_factory:
        mock_p = MagicMock()
        mock_factory.return_value = mock_p
        mock_p.get_model_name.return_value = "test-model"
        
        # Mock settings to change persona
        with patch('src.analyzer.gemini_analyzer.KakeiboAnalyzer._get_active_persona', return_value=persona):
            analyzer = KakeiboAnalyzer()

            transactions = [
                Transaction(
                    transaction_id="tx_1",
                    transaction_date=date(2024, 1, 1),
                    category="食費",
                    genre="外食",
                    amount=15000,
                    comment="高いお肉",
                    source="test",
                    mode="payment"
                )
            ]
            assets = [{"category": "現金", "amount": 100000}]
            profile = {
                "user": {
                    "name": "テスト太郎",
                    "occupation": "エンジニア",
                    "hobbies": ["読書"],
                    "investment_policy": "保守的",
                    "target": {"date": "2025-01-01", "description": "100万円貯める"}
                }
            }
            budget = {"monthly": {"categories": {"食費": 10000}}}

            analyzer.analyze_kakeibo(transactions, assets, "monthly", profile, budget)

            args, kwargs = mock_p.generate_content.call_args
            print(f"\n=== PERSONA: {persona} ===")
            print("--- SYSTEM PROMPT ---")
            print(kwargs['system_prompt'])
            print("--- USER PROMPT ---")
            print(kwargs['user_prompt'])

if __name__ == "__main__":
    for persona in ["gal", "butler", "zen"]:
        test_prompt_content(persona)
