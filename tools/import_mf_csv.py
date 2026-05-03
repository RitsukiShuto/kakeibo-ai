import sys
import os
import pandas as pd
from datetime import datetime
import argparse

# プロジェクトのルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import Database
from src.models import Transaction

def import_csv(file_path: str, db_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Reading CSV: {file_path}")
    try:
        # マネーフォワードのCSVは通常 cp932 (Shift-JIS)
        df = pd.read_csv(file_path, encoding="cp932")
    except Exception as e:
        print(f"Error reading CSV with cp932: {e}")
        print("Retrying with utf-8...")
        df = pd.read_csv(file_path, encoding="utf-8")

    def find_col(possible_names):
        for col in df.columns:
            if any(name in col for name in possible_names):
                return col
        return None

    col_id = find_col(["ID"])
    col_date = find_col(["日付"])
    col_content = find_col(["内容"])
    col_amount = find_col(["金額"])
    col_major = find_col(["大項目"])
    col_minor = find_col(["中項目"])
    col_calc = find_col(["計算対象"])

    # 必須列のチェック
    required = {"日付": col_date, "金額": col_amount, "大項目": col_major}
    missing = [k for k, v in required.items() if v is None]
    if missing:
        print(f"Error: Required columns missing: {missing}")
        return

    db = Database(db_path=db_path)
    transactions = []

    print("Parsing rows...")
    for _, row in df.iterrows():
        # 計算対象外（振替など）の除外
        if col_calc and str(row[col_calc]) == "0":
            continue
        
        try:
            amount_val = str(row[col_amount]).replace(",", "")
            amount = int(float(amount_val))
            
            # 日付のパース
            date_str = str(row[col_date])
            try:
                dt = datetime.strptime(date_str, "%Y/%m/%d").date()
            except ValueError:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()

            transactions.append(Transaction(
                transaction_id=str(row[col_id]) if col_id and pd.notna(row[col_id]) else None,
                transaction_date=dt,
                category=str(row[col_major]) if col_major else "未分類",
                genre=str(row[col_minor]) if col_minor else "",
                amount=abs(amount),
                comment=str(row[col_content]) if col_content else "",
                source="MoneyForward_Import",
                mode="payment" if amount < 0 else "income"
            ))
        except Exception as e:
            print(f"Skipping row due to error: {e} | Row: {row.to_dict()}")

    if transactions:
        print(f"Saving {len(transactions)} transactions to database...")
        db.save_transactions(transactions)
        print("Import completed successfully!")
    else:
        print("No valid transactions found to import.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import MoneyForward CSV to Database")
    parser.add_argument("file", help="Path to the MoneyForward CSV file")
    parser.add_argument("--db", default="data/kakeibo.db", help="Path to the SQLite database")
    
    args = parser.parse_args()
    import_csv(args.file, args.db)
