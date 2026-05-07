import sqlite3
import os
from datetime import date
from src.db.database import Database
from src.models import Transaction

def test_reimbursement_columns():
    db_path = "local/test_reimbursement.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path=db_path)
    
    # 1. 正常なトランザクションの保存
    t1 = Transaction(
        transaction_id="test_1",
        transaction_date=date(2026, 5, 1),
        category="食費",
        genre="飲み会",
        amount=20000,
        comment="飲み会立替",
        source="mf",
        mode="payment",
        self_amount=5000,
        is_reimbursement=1,
        reimbursement_status="pending"
    )
    
    db.save_transactions([t1])
    
    # 2. データの取得検証
    txs = db.get_transactions_range(date(2026, 5, 1), date(2026, 5, 1))
    assert len(txs) == 1
    retrieved = txs[0]
    
    assert retrieved.amount == 20000
    assert retrieved.self_amount == 5000
    assert retrieved.is_reimbursement == 1
    assert retrieved.reimbursement_status == "pending"
    
    # 3. UPSERTの検証（ステータス更新）
    t1_updated = t1.model_copy(update={"reimbursement_status": "completed"})
    db.save_transactions([t1_updated])
    
    txs_updated = db.get_transactions_range(date(2026, 5, 1), date(2026, 5, 1))
    assert txs_updated[0].reimbursement_status == "completed"
    
    # 4. COALESCEの検証（新しい保存でNULLを指定しても既存の値が維持されるか）
    # ※現在のsave_transactionsの実装では、Transactionモデルのデフォルト（None）が渡されるため、
    # COALESCEにより既存の値が維持されるはず。
    t1_partial = Transaction(
        transaction_id="test_1",
        transaction_date=date(2026, 5, 1),
        category="食費",
        amount=20000,
        source="mf",
        mode="payment"
        # self_amount, is_reimbursementなどは指定しない(None)
    )
    db.save_transactions([t1_partial])
    txs_coalesce = db.get_transactions_range(date(2026, 5, 1), date(2026, 5, 1))
    assert txs_coalesce[0].self_amount == 5000
    assert txs_coalesce[0].reimbursement_status == "completed"

    print("✅ Database reimbursement columns test passed!")
    
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    test_reimbursement_columns()
