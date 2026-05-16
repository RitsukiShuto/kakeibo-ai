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
            genre TEXT,
            amount INTEGER,
            comment TEXT,
            source TEXT,
            mode TEXT,
            is_reimbursement INTEGER DEFAULT 0,
            self_amount INTEGER,
            reimbursement_status TEXT
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
    cursor.execute("INSERT INTO transactions VALUES ('t1', ?, '食費', '外食', 1000, 'ランチ', 'mf', 'payment', 0, NULL, NULL)", (today,))
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
    
    settings_data = {
        "ai": {
            "active_model": "gemini-2.0-flash",
            "available_models": [
                {"id": "gemini-2.0-flash", "name": "Model A", "description": "Desc A"},
                {"id": "gemini-1.5-pro", "name": "Model B", "description": "Desc B"}
            ]
        }
    }
    with open(os.path.join(TEST_CONFIG_DIR, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings_data, f)
    with open(os.path.join(TEST_CONFIG_DIR, "settings.json.example"), "w", encoding="utf-8") as f:
        json.dump(settings_data, f)
        
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

def test_get_kpi_with_timeframe():
    response = client.get("/api/kpi?timeframe=daily")
    assert response.status_code == 200
    data = response.json()
    assert "budget" in data
    assert "actual" in data

def test_old_format_budget_compatibility():
    """旧形式のbudget.jsonでもカテゴリが個別に展開されることを確認"""
    config_dir = os.environ["KAKEIBO_CONFIG_DIR"]
    old_budget = {
        "monthly": {
            "income": 200000,
            "categories": {
                "食費": 30000,
                "住宅": 50000,
                "交際費": 10000
            }
        }
    }
    with open(os.path.join(config_dir, "budget.json"), "w", encoding="utf-8") as f:
        json.dump(old_budget, f)
    
    response = client.get("/api/budget-actual")
    assert response.status_code == 200
    data = response.json()
    # 旧形式でも各カテゴリが個別に表示される（「その他」に統合されない）
    categories = [item["category"] for item in data]
    assert "食費" in categories
    assert "住宅" in categories
    assert "交際費" in categories
    assert "その他" not in categories
    
    # テスト後に元のbudget.jsonに戻す
    new_budget = {"monthly": {"budget": {"variable": {"食費": 30000}}}}
    with open(os.path.join(config_dir, "budget.json"), "w", encoding="utf-8") as f:
        json.dump(new_budget, f)

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

def test_get_ai_models():
    response = client.get("/api/settings/ai-models")
    assert response.status_code == 200
    data = response.json()
    assert "active_model" in data
    assert "available_models" in data
    assert len(data["available_models"]) > 0

def test_update_active_model():
    # モデルの更新テスト
    update_data = {"active_model": "gemini-1.5-pro"}
    response = client.put("/api/settings/active-model", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    # 更新されたことを確認
    response = client.get("/api/settings/ai-models")
    assert response.json()["active_model"] == "gemini-1.5-pro"

def test_get_life_plan_simulation():
    # プロファイルにライフプラン設定を追加
    config_dir = os.environ["KAKEIBO_CONFIG_DIR"]
    profile_path = os.path.join(config_dir, "profile.json")
    profile_data = {
        "user": {
            "life_plan": {
                "current_age": 30,
                "retirement_age": 65,
                "annual_return_rate": 3.0,
                "annual_inflation_rate": 1.0,
                "monthly_living_expenses_post_retirement": 200000,
                "events": []
            }
        }
    }
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f)
        
    response = client.get("/api/life-plan/simulation")
    assert response.status_code == 200
    data = response.json()
    assert "trajectory" in data
    assert "settings" in data
    assert data["advice"] is None # アドバイスは別エンドポイントになったためNone

def test_get_life_plan_advice():
    response = client.get("/api/life-plan/advice")
    assert response.status_code == 200
    data = response.json()
    assert "advice" in data
    assert data["advice"] == "将来の資産推移は良好です。このままの貯蓄ペースを維持しましょう！💅✨"

def test_transaction_crud():
    # 1. Create
    new_tx = {
        "transaction_date": "2026-05-18",
        "category": "テスト費",
        "genre": "検証",
        "amount": 1000,
        "comment": "API CRUD TEST",
        "source": "api_test",
        "mode": "payment",
        "is_reimbursement": 0
    }
    response = client.post("/api/transactions", json=new_tx)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    tx_id = res_data["transaction_id"]
    
    # 2. Read
    response = client.get(f"/api/transactions?search=API CRUD TEST")
    assert response.status_code == 200
    data = response.json()
    assert any(t["transaction_id"] == tx_id for t in data)
    
    # 3. Update
    update_data = {"comment": "API CRUD TEST UPDATED"}
    response = client.put(f"/api/transactions/{tx_id}", json=update_data)
    assert response.status_code == 200
    
    # 4. Delete
    response = client.delete(f"/api/transactions/{tx_id}")
    assert response.status_code == 200
    
    # Verify delete
    response = client.get(f"/api/transactions?search=API CRUD TEST UPDATED")
    all_ids = [t["transaction_id"] for t in response.json()]
    assert tx_id not in all_ids

def test_env_settings():
    response = client.get("/api/settings/env")
    assert response.status_code == 200
    data = response.json()
    assert "LLM_PROVIDER" in data

def test_csv_import_format_check():
    # Invalid file type
    files = {'file': ('test.txt', b'hello', 'text/plain')}
    response = client.post("/api/import/csv", files=files)
    assert response.status_code == 400
