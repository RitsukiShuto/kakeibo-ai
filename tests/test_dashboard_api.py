import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from datetime import datetime, timedelta
import os
import json
import sqlite3
from src.api.utils import get_db_path, get_config_dir

client = TestClient(app)

@pytest.fixture
def mock_db_and_budget(tmp_path):
    # Setup temporary db
    db_path = tmp_path / "test_kakeibo.db"
    os.environ["KAKEIBO_DB_PATH"] = str(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE transactions (
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
    cursor.execute("""
        CREATE TABLE analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timeframe TEXT NOT NULL,
            summary TEXT,
            body TEXT,
            report_path TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert mock data
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Transactions
    cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   ("tx1", today, "食費", "外食", 1000, "ランチ", "manual", "payment", None, 0, None, today))
    cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   ("tx2", yesterday, "給与", "", 300000, "1月分", "manual", "income", None, 0, None, yesterday))
    
    # Analysis History
    cursor.execute("INSERT INTO analysis_history (timeframe, summary, body, report_path, score, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   ("monthly", "今月は食費が少し多いです。節約しましょう。", "食費が先月比15%増加。外食を減らしてみましょう。", "reports/test.md", 80, today))
    
    conn.commit()
    conn.close()

    # Setup temporary budget.json
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    os.environ["KAKEIBO_CONFIG_DIR"] = str(config_dir)
    budget_file = config_dir / "budget.json"
    budget_data = {
        "monthly": {
            "budget": {
                "fixed": {
                    "住居費": 50000
                },
                "variable": {
                    "食費": 30000,
                    "交際費": 10000
                }
            }
        }
    }
    with open(budget_file, "w", encoding="utf-8") as f:
        json.dump(budget_data, f)

    yield str(db_path), str(config_dir)
    
    # Cleanup
    if "KAKEIBO_DB_PATH" in os.environ:
        del os.environ["KAKEIBO_DB_PATH"]
    if "KAKEIBO_CONFIG_DIR" in os.environ:
        del os.environ["KAKEIBO_CONFIG_DIR"]

def test_get_stats_flow(mock_db_and_budget):
    response = client.get("/api/stats/flow")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) > 0
    assert len(data["links"]) > 0

def test_get_budget_actual_with_timeframe(mock_db_and_budget):
    # Test default (monthly)
    response = client.get("/api/budget-actual")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Test weekly
    response = client.get("/api/budget-actual?timeframe=weekly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check if pace_limit is present
    for item in data:
        assert "pace_limit" in item

def test_get_analysis_history_latest_summary(mock_db_and_budget):
    response = client.get("/api/analysis-history/latest-summary")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "body" in data
    assert data["summary"] == "今月は食費が少し多いです。節約しましょう。"
    assert data["body"] == "食費が先月比15%増加。外食を減らしてみましょう。"

def test_get_analysis_history_form(mock_db_and_budget):
    response = client.get("/api/analysis-history/form")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("status" in item for item in data)
    assert all("start_date" in item for item in data)
    assert all(item["status"] in ["W", "L", "D", "-"] for item in data)
