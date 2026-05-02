import sqlite3
import json

def inspect_db():
    db_path = "data/kakeibo.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Analysis History ---")
    cursor.execute("SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Timeframe: {row['timeframe']}")
        print(f"Summary: {row['summary']}")
        print(f"Raw Response: {row['raw_response']}")
    else:
        print("No analysis history found.")

    print("\n--- Recent Assets ---")
    cursor.execute("SELECT * FROM assets ORDER BY acquired_date DESC, institution LIMIT 20")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Date: {row['acquired_date']}, Type: {row['asset_type']}, Amount: {row['amount']}, Institution: {row['institution']}")

    conn.close()

if __name__ == "__main__":
    inspect_db()
