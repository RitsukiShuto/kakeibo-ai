import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from src.analyzer.gemini_analyzer import GeminiAnalyzer
from src.models import Transaction

@pytest.fixture
def mock_genai():
    with patch('src.analyzer.gemini_analyzer.genai') as mock:
        yield mock

def test_analyze_kakeibo_success(mock_genai):
    # Mock model response
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_genai.list_models.return_value = [MagicMock(name='models/gemini-2.0-flash', supported_generation_methods=['generateContent'])]
    
    mock_response = MagicMock()
    mock_response.text = '''{
        "slack_summary": "テストサマリー",
        "obsidian_report": "# テストレポート",
        "actions": [{"command": "KEEP", "description": "いい感じ"}],
        "asset_breakdown": [{"category": "現金", "amount": 100}],
        "budget_status": [{"category": "食費", "budget": 1000, "actual": 500, "status": "OK"}],
        "totonoi_score": 80,
        "savings_potential": 500
    }'''
    mock_model.generate_content.return_value = mock_response

    analyzer = GeminiAnalyzer()
    
    transactions = [
        Transaction(
            transaction_date=date(2024, 1, 1),
            category="食費",
            amount=500,
            source="test",
            mode="payment"
        )
    ]
    assets = [{"category": "現金", "amount": 100}]
    profile = {"user": {"target": {}}}
    budget = {"monthly": {"categories": {"食費": 1000}}}

    result = analyzer.analyze_kakeibo(transactions, assets, "monthly", profile, budget)

    assert result.slack_summary == "テストサマリー"
    assert result.totonoi_score == 80
    assert len(result.budget_status) == 1
    assert result.budget_status[0].category == "食費"
    mock_model.generate_content.assert_called_once()

def test_analyze_kakeibo_failure(mock_genai):
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.generate_content.side_effect = Exception("API Error")

    analyzer = GeminiAnalyzer()
    result = analyzer.analyze_kakeibo([], [], "monthly", {"user": {"target": {}}})

    assert result is None
