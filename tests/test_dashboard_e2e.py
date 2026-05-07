import os
import sqlite3
import time
from playwright.sync_api import sync_playwright
from datetime import date

# テスト用DBの設定
DB_PATH = "local/test_dashboard.db"

def setup_test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 必要なテーブルの作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            transaction_date TEXT NOT NULL,
            category TEXT NOT NULL,
            genre TEXT,
            amount INTEGER NOT NULL,
            comment TEXT,
            source TEXT NOT NULL,
            mode TEXT NOT NULL,
            self_amount INTEGER,
            is_reimbursement INTEGER DEFAULT 0,
            reimbursement_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # テストデータの挿入
    today = date.today().isoformat()
    cursor.execute("""
        INSERT INTO transactions (transaction_id, transaction_date, category, amount, comment, source, mode)
        VALUES ('tx_1', ?, '食費', 20000, '飲み会立替用', 'mf', 'payment')
    """, (today,))
    
    conn.commit()
    conn.close()

def test_dashboard_e2e():
    setup_test_db()
    
    # Streamlitを別プロセスで起動するのは複雑なため、
    # ユーザーがダッシュボードを起動していることを前提とするか、
    # ここではPlaywrightでURLにアクセスしてUI要素を確認するロジックを記述します。
    # ※実際のCI等では背景プロセスで起動する必要があります。

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Accessing Dashboard...")
            page.goto("http://localhost:8501", timeout=10000)
            
            # タイトルの確認
            page.wait_for_selector("text=Kakeibo AI Integrated Dashboard")
            print("✅ Dashboard title found.")

            # 立替セクションの確認
            page.wait_for_selector("text=AI Expense Splitter")
            print("✅ AI Expense Splitter section found.")

            # 明細選択セレクトボックスの確認（Duplicate ID エラーが出ていないか）
            selectboxes = page.query_selector_all('div[data-baseweb="select"]')
            if len(selectboxes) > 0:
                print(f"✅ Found {len(selectboxes)} selectboxes.")
            else:
                raise Exception("Selectboxes not found.")

            # 立替設定の操作シミュレーション（オプション）
            # ここでは単純な表示確認にとどめます
            
            print("E2E Test completed successfully!")

        except Exception as e:
            print(f"❌ E2E Test failed: {e}")
            # エラー時のスクリーンショット
            page.screenshot(path="logs/e2e_error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    # 注意: このテストを実行する前に `streamlit run dashboard.py` を起動しておく必要があります。
    # また、DB_PATHをテスト用に切り替えて起動する必要があります。
    test_dashboard_e2e()
