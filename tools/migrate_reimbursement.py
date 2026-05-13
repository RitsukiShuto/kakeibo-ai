import sqlite3
import os

def migrate():
    local_dir = os.getenv("KAKEIBO_LOCAL_DIR", "local")
    db_path = f"{local_dir}/kakeibo.db"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking transactions table for new columns...")
    
    # 追加するカラムのリスト
    # self_amount: 自己負担額 (デフォルトはNULL。立替設定時のみ値が入る)
    # is_reimbursement: 立替フラグ (0: 通常, 1: 立替)
    # reimbursement_status: 精算ステータス (pending, partial, completed)
    
    new_columns = [
        ("self_amount", "INTEGER"),
        ("is_reimbursement", "INTEGER DEFAULT 0"),
        ("reimbursement_status", "TEXT")
    ]

    # 既存のカラムを取得
    cursor.execute("PRAGMA table_info(transactions)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            print(f"Adding column {col_name} to transactions table...")
            cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
