import pytest
from unittest.mock import MagicMock
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(autouse=True)
def mock_kakeibo_analyzer(monkeypatch):
    """
    全てのテストで KakeiboAnalyzer を自動的にモック化し、
    意図しない API 呼び出しと課金を防ぐ。
    """
    from src.analyzer.gemini_analyzer import KakeiboAnalyzer
    
    mock_instance = MagicMock()
    
    # analyze_kakeibo のデフォルトレスポンス
    from src.models import AIResponse
    mock_ai_response = AIResponse(
        summary="今月は順調！節約ペース良好🎉",
        body="食費は先月比10%減。自炊を増やしたことが主因です。来月は交通費に注意しましょう。",
        slack_report="ギャル風のテストレポートだよ！✨",
        obsidian_report="## テストレポート\n分析内容は正常です。",
        actions=[{"command": "Keep", "description": "このまま頑張って！"}],
        asset_breakdown=[{"category": "現金", "amount": 100000}],
        budget_status=[{"category": "食費", "budget": 30000, "actual": 25000, "status": "適正"}],
        totonoi_score=85,
        savings_potential=5000
    )
    mock_instance.analyze_kakeibo.return_value = mock_ai_response
    
    # parse_reimbursement_text のデフォルトレスポンス
    mock_instance.parse_reimbursement_text.return_value = {"self_amount": 1000, "reason": "割り勘のテスト"}
    
    # detect_potential_reimbursements のデフォルトレスポンス
    mock_instance.detect_potential_reimbursements.return_value = [
        {"transaction_id": "test_id", "reason": "高額なため", "confidence": 0.9}
    ]

    # analyze_life_plan のデフォルトレスポンス
    mock_instance.analyze_life_plan.return_value = "将来の資産推移は良好です。このままの貯蓄ペースを維持しましょう！💅✨"
    
    # chat のデフォルトレスポンス
    mock_instance.chat.return_value = "チャットのテスト回答だよ！✨"

    # クラスごと差し替え
    monkeypatch.setattr("src.analyzer.gemini_analyzer.KakeiboAnalyzer", lambda: mock_instance)
    monkeypatch.setattr("src.analyzer.gemini_analyzer.GeminiAnalyzer", lambda: mock_instance)
    
    return mock_instance

@pytest.fixture
def mock_db(tmp_path):
    """
    テスト用の空のデータベースを提供する。
    """
    from src.db.database import Database
    db_path = str(tmp_path / "test_kakeibo.db")
    return Database(db_path=db_path)
