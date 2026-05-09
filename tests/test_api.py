import os
import json
import sqlite3
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from datetime import date

# テスト用ディレクトリとDBの設定
TEST_DB_PATH = "local/test_api.db"
TEST_CONFIG_DIR = "tests/config"

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # 環境変数の設定
    os.environ["KAKEIBO_DB_PATH"] = TEST_DB_PATH
    os.environ["KAKEIBO_CONFIG_DIR"] = TEST_CONFIG_DIR
    
    # ディレクトリの作成
    os.makedirs(TEST_CONFIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(TEST_DB_PATH), exist_ok=True)
    
    # DBの初期化
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE transactions (
            transaction_id TEXT PRIMARY KEY,
            transaction_date TEXT,
            category TEXT,
            amount INTEGER,
            comment TEXT,
            source TEXT,
            mode TEXT,
            is_reimbursement INTEGER DEFAULT 0,
            self_amount INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acquired_date TEXT,
            asset_type TEXT,
            amount INTEGER,
            source TEXT,
            institution TEXT
        )
    """)
    
    # テストデータの投入
    today = date.today().isoformat()
    cursor.execute("INSERT INTO transactions VALUES ('t1', ?, '食費', 1000, 'ランチ', 'mf', 'payment', 0, NULL)", (today,))
    cursor.execute("INSERT INTO assets (acquired_date, asset_type, amount, source, institution) VALUES (?, '銀行', 500000, 'mf', '銀行A')", (today,))
    
    conn.commit()
    conn.close()
    
    # 設定ファイルの作成
    budget_data = {
        "monthly": {
            "budget": {
                "variable": {
                    "食費": 30000
                }
            }
        }
    }
    with open(os.path.join(TEST_CONFIG_DIR, "budget.json"), "w", encoding="utf-8") as f:
        json.dump(budget_data, f)
        
    yield
    
    # 後片付け
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Kakeibo AI API is running"}

def test_get_kpi():
    response = client.get("/api/kpi")
    assert response.status_code == 200
    data = response.json()
    assert "budget" in data
    assert "actual" in data
    assert data["actual"] == 1000
    assert data["total_assets"] == 500000

def test_get_transactions():
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["category"] == "食費"

def test_update_transaction():
    # 更新前のデータ確認
    response = client.get("/api/transactions")
    tx_id = response.json()[0]["transaction_id"]
    
    # 更新実行
    update_data = {"category": "外食", "comment": "更新テスト"}
    response = client.put(f"/api/transactions/{tx_id}", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    # 更新後のデータ確認
    response = client.get("/api/transactions")
    updated_tx = response.json()[0]
    assert updated_tx["category"] == "外食"
    assert updated_tx["comment"] == "更新テスト"

def test_get_budget_actual():
    response = client.get("/api/budget-actual")
    assert response.status_code == 200
    data = response.json()
    
    # 前のテストで「食費」が「外食」に更新されたため、食費の実績は 0 になる
    food_budget = next((item for item in data if item["category"] == "食費"), None)
    assert food_budget is not None
    assert food_budget["budget"] == 30000
    assert food_budget["actual"] == 0

    # 外食（実績1000円）を確認
    # ただし外食は予算に含まれていないので、get_budget_actual の現在のロジックでは
    # 予算設定にあるカテゴリのみが返される。
