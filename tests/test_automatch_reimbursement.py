import os
import sqlite3
from datetime import date
from src.db.database import Database
from src.models import Transaction

def test_auto_match_reimbursement():
    db_path = "local/test_automatch.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path=db_path)
    
    # 1. 立替明細（20,000円、自己負担5,000円 -> 15,000円回収予定）を登録
    t_out = Transaction(
        transaction_id="tx_out",
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
    
    # 2. 入金明細（15,000円）を登録
    t_in = Transaction(
        transaction_id="tx_in",
        transaction_date=date(2026, 5, 3),
        category="未分類",
        amount=15000,
        comment="PayPayマネー",
        source="mf",
        mode="income"
    )
    
    db.save_transactions([t_out, t_in])
    
    # マッチング実行前
    txs_pre = db.get_transactions_range(date(2026, 5, 1), date(2026, 5, 1))
    assert txs_pre[0].reimbursement_status == "pending"
    
    # 自動マッチング実行
    matched_count = db.auto_match_reimbursements()
    assert matched_count == 1
    
    # マッチング実行後
    txs_post = db.get_transactions_range(date(2026, 5, 1), date(2026, 5, 1))
    assert txs_post[0].reimbursement_status == "completed"
    
    print("✅ Auto-match reimbursement test passed!")
    
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    test_auto_match_reimbursement()
