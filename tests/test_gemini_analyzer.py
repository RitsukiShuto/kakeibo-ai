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

def test_daily_prompt_includes_date_info(mock_provider, mock_env):
    """daily timeframe が集計日・残り日数・固定費情報を含むことをテスト"""
    mock_provider.get_model_name.return_value = "gemini-2.0-flash"
    mock_provider.generate_content.return_value = '''{
        "slack_report": "テスト詳細レポート",
        "obsidian_report": "# テストレポート",
        "actions": [],
        "asset_breakdown": [],
        "budget_status": [],
        "totonoi_score": 80,
        "savings_potential": 0
    }'''

    analyzer = KakeiboAnalyzer()

    # daily 用の budget: fixed と variable を定義
    budget = {
        "monthly": {
            "budget": {
                "fixed": {"家賃": 80000, "光熱費": 10000, "通信費": 5000},
                "variable": {"食費": 30000, "交際費": 10000}
            }
        }
    }
    profile = {"user": {"target": {}}}

    with patch('src.analyzer.gemini_analyzer.datetime') as mock_datetime:
        # 日付を固定（5月15日）
        from datetime import datetime as real_datetime
        mock_datetime.now.return_value = real_datetime(2024, 5, 15)
        mock_datetime.side_effect = lambda *args, **kw: real_datetime(*args, **kw)

        result = analyzer.analyze_kakeibo([], [], "daily", profile, budget)

    assert result is not None
    # generate_content が呼ばれたか確認
    mock_provider.generate_content.assert_called_once()
    
    # 呼び出し引数を取得して、daily 専用情報が含まれているか確認
    call_args = mock_provider.generate_content.call_args
    user_prompt = call_args.kwargs.get('user_prompt', '')
    
    assert "集計基準日" in user_prompt
    assert "今月の残り日数" in user_prompt
    assert "固定費合計" in user_prompt
    assert "95,000" in user_prompt  # 80000+10000+5000 = 95000
