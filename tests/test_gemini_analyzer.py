import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from src.analyzer.gemini_analyzer import KakeiboAnalyzer
from src.models import Transaction

@pytest.fixture
def mock_provider():
    with patch('src.analyzer.providers.factory.LLMFactory.create_provider') as mock_factory:
        mock_p = MagicMock()
        mock_factory.return_value = mock_p
        yield mock_p

@pytest.fixture
def mock_env():
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'fake_key', 'LLM_PROVIDER': 'gemini'}):
        yield

def test_analyze_kakeibo_success(mock_provider, mock_env):
    mock_provider.get_model_name.return_value = "gemini-2.0-flash"
    mock_provider.generate_content.return_value = '''{
        "slack_report": "テスト詳細レポート",
        "obsidian_report": "# テストレポート",
        "actions": [{"command": "KEEP", "description": "いい感じ"}],
        "asset_breakdown": [{"category": "現金", "amount": 100}],
        "budget_status": [{"category": "食費", "budget": 1000, "actual": 500, "status": "OK"}],
        "totonoi_score": 80,
        "savings_potential": 500
    }'''

    analyzer = KakeiboAnalyzer()

    transactions = [
        Transaction(
            transaction_id="tx_1",
            transaction_date=date(2024, 1, 1),
            category="食費",
            genre="外食",
            amount=500,
            source="test",
            mode="payment"
        )
    ]
    assets = [{"category": "現金", "amount": 100}]
    profile = {"user": {"target": {}}}
    budget = {"monthly": {"categories": {"食費": 1000}}}

    result = analyzer.analyze_kakeibo(transactions, assets, "monthly", profile, budget)

    assert result.slack_report == "テスト詳細レポート"
    assert result.totonoi_score == 80
    assert len(result.budget_status) == 1
    assert result.budget_status[0].category == "食費"
    mock_provider.generate_content.assert_called_once()

def test_analyze_kakeibo_failure(mock_provider, mock_env):
    mock_provider.get_model_name.return_value = "gemini-2.0-flash"
    mock_provider.generate_content.side_effect = Exception("API Error")

    analyzer = KakeiboAnalyzer()
    result = analyzer.analyze_kakeibo([], [], "monthly", {"user": {"target": {}}})

    assert result is None
