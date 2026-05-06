import pytest
import time
from datetime import date, timedelta
from src.db.database import Database
from src.models import Transaction, Asset

@pytest.fixture
def db():
    # テスト用にインメモリDBを使用
    test_db = Database(":memory:")
    return test_db

def test_save_and_get_transactions(db):
    t = Transaction(
        transaction_id="t1",
        transaction_date=date.today(),
        category="食費",
        amount=1000,
        source="Test",
        mode="payment"
    )
    db.save_transactions([t])
    
    # 最初は分析履歴がないので、全ての明細が「新しい」と判定されるはず
    new_items = db.get_new_transactions_since_last_analysis("weekly")
    assert len(new_items) == 1
    assert new_items[0].transaction_id == "t1"

def test_upsert_transaction(db):
    t1 = Transaction(
        transaction_id="dup",
        transaction_date=date.today(),
        category="食費",
        amount=1000,
        source="Test",
        mode="payment"
    )
    db.save_transactions([t1])
    
    # 同じIDで金額を変更して保存
    t2 = t1.model_copy(update={"amount": 2000})
    db.save_transactions([t2])
    
    # DBから直接確認
    items = db.get_new_transactions_since_last_analysis("weekly")
    assert len(items) == 1
    assert items[0].amount == 2000

def test_save_and_get_assets(db):
    a1 = Asset(
        acquired_date=date.today(),
        asset_type="預金",
        amount=500000,
        source="Test",
        institution="BankA"
    )
    db.save_assets([a1])
    
    summary = db.get_asset_category_summary()
    assert len(summary) == 1
    assert summary[0]["category"] == "預金"
    assert summary[0]["amount"] == 500000

def test_asset_duplication_prevention(db):
    # 同じ日の同じ金融機関のデータを2回保存しても、重複しないこと
    a = Asset(
        acquired_date=date.today(),
        asset_type="預金",
        amount=500000,
        source="Test",
        institution="BankA"
    )
    db.save_assets([a])
    db.save_assets([a])
    
    summary = db.get_asset_category_summary()
    assert summary[0]["amount"] == 500000
    
    items = db.get_current_asset_summary()
    assert len(items) == 1

def test_analysis_history_and_diff_logic(db):
    # 1. 最初の明細を保存
    t1 = Transaction(transaction_id="old", transaction_date=date.today()-timedelta(days=1), category="A", amount=100, source="S", mode="p")
    db.save_transactions([t1])
    
    # 2. 最初の分析を実行して履歴を保存
    db.save_analysis("weekly", "Summary 1", "path1", 80, "{}")
    
    # 秒単位の精度問題を回避するため少し待機
    time.sleep(1.1)
    
    # 3. 新しい明細を追加
    t2 = Transaction(transaction_id="new", transaction_date=date.today(), category="B", amount=200, source="S", mode="p")
    db.save_transactions([t2])
    
    # 4. 「新しい明細」だけが取得されることを確認
    new_items = db.get_new_transactions_since_last_analysis("weekly")
    assert len(new_items) == 1
    assert new_items[0].transaction_id == "new"

def test_get_transactions_range(db):
    # テストデータの準備（3月と4月の明細）
    t1 = Transaction(transaction_id="mar", transaction_date=date(2024,3,15), category="C", amount=1, source="S", mode="p")
    t2 = Transaction(transaction_id="apr1", transaction_date=date(2024,4,1), category="C", amount=1, source="S", mode="p")
    t3 = Transaction(transaction_id="apr15", transaction_date=date(2024,4,15), category="C", amount=1, source="S", mode="p")
    t4 = Transaction(transaction_id="may", transaction_date=date(2024,5,1), category="C", amount=1, source="S", mode="p")
    db.save_transactions([t1, t2, t3, t4])
    
    # 4月1日から4月30日までの範囲で取得
    results = db.get_transactions_range(date(2024,4,1), date(2024,4,30))
    
    assert len(results) == 2
    ids = [r.transaction_id for r in results]
    assert "apr1" in ids
    assert "apr15" in ids
    assert "mar" not in ids
    assert "may" not in ids
