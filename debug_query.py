import sqlite3
import pandas as pd
from datetime import datetime

def test_query():
    conn = sqlite3.connect('local/kakeibo.db')
    current_month = datetime.now().strftime("%Y-%m")
    query = f"SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment'"
    df = pd.read_sql_query(query, conn)
    print(f"Current Month: {current_month}")
    print(df)
    conn.close()

if __name__ == "__main__":
    test_query()
