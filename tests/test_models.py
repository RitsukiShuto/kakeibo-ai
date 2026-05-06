import pytest
from datetime import date
from pydantic import ValidationError
from src.models import Transaction, Asset, AIResponse, AIAction, AssetBreakdown

def test_transaction_validation():
    # 正常系
    t = Transaction(
        transaction_date=date.today(),
        category="食費",
        amount=1000,
        source="Test",
        mode="payment"
    )
    assert t.amount == 1000

    # 異常系 (型違い)
    with pytest.raises(ValidationError):
        Transaction(
            transaction_date="not-a-date",
            category="食費",
            amount="not-a-number",
            source="Test",
            mode="payment"
        )

def test_ai_response_validation():
    # 正常系テスト
    resp = AIResponse(
        slack_report="Full report text",
        obsidian_report="# Report",
        actions=[AIAction(command="Cmd", description="Desc")],
        asset_breakdown=[AssetBreakdown(category="Cash", amount=100)],
        totonoi_score=90,
        savings_potential=500
    )
    assert resp.slack_report == "Full report text"

    assert len(resp.asset_breakdown) == 1
