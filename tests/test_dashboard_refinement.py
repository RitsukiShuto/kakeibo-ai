import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.utils import get_db_path, get_config_dir, load_budget
import os
import json
import sqlite3
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture
def mock_db_and_config(tmp_path):
    # Setup temporary DB and config
    db_path = tmp_path / "test_kakeibo.db"
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create tables
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY,
        transaction_date TEXT,
        amount INTEGER,
        mode TEXT,
        category TEXT,
        genre TEXT,
        source TEXT,
        is_reimbursement INTEGER,
        self_amount INTEGER
    )
    """)
    
    # Insert some income
    cursor.execute("INSERT INTO transactions (transaction_date, amount, mode, category, genre, source) VALUES (?, ?, ?, ?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d"), 500000, "income", "収入", "給与", "MoneyForward"))
    cursor.execute("INSERT INTO transactions (transaction_date, amount, mode, category, genre, source) VALUES (?, ?, ?, ?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d"), 10000, "income", "収入", "配当所得", "MoneyForward"))
    cursor.execute("INSERT INTO transactions (transaction_date, amount, mode, category, genre, source) VALUES (?, ?, ?, ?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d"), 5000, "income", "収入", "その他入金", "MoneyForward"))

    # Insert some expenses (Fixed and Variable)
    # Variable: 食費
    # Fixed: 住居
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO transactions (transaction_date, amount, mode, category, genre, source, is_reimbursement) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (today, 1000, "payment", "食費", "食料品", "Cash", 0))
    cursor.execute("INSERT INTO transactions (transaction_date, amount, mode, category, genre, source, is_reimbursement) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (today, 100000, "payment", "住居", "家賃", "Bank", 0))
    
    conn.commit()
    conn.close()
    
    # Create budget.json
    budget_data = {
        "monthly": {
            "budget": {
                "fixed": {
                    "住居": 100000
                },
                "variable": {
                    "食費": 30000
                }
            }
        }
    }
    with open(config_dir / "budget.json", "w", encoding="utf-8") as f:
        json.dump(budget_data, f)
        
    # Mock environment variables
    os.environ["KAKEIBO_DB_PATH"] = str(db_path)
    os.environ["KAKEIBO_CONFIG_DIR"] = str(config_dir)
    
    yield str(db_path), str(config_dir)
    
    # Cleanup
    if "KAKEIBO_DB_PATH" in os.environ: del os.environ["KAKEIBO_DB_PATH"]
    if "KAKEIBO_CONFIG_DIR" in os.environ: del os.environ["KAKEIBO_CONFIG_DIR"]

def test_weekly_form_filtering(mock_db_and_config):
    # Before update, it includes all categories.
    # Total monthly budget = 100000 (fixed) + 30000 (variable) = 130000
    # Weekly budget = 130000 * 12 / 52 = 30000
    # Actual expense = 1000 (食費) + 100000 (住居) = 101000
    # This should be an 'L' (Loss) because 101000 > 30000.
    
    # AFTER update, it should only include variable categories.
    # Total monthly budget = 30000
    # Weekly budget = 30000 * 12 / 52 = 6923
    # Actual expense = 1000
    # This should be a 'W' (Win) because 1000 <= 6923.
    
    response = client.get("/api/analysis-history/form")
    assert response.status_code == 200
    data = response.json()
    
    # The current week is the last item in results.append
    current_week = data[-1]
    # If the fix is NOT applied, this might be 'L' because it includes the 100000 rent.
    # If the fix IS applied, it should be 'W'.
    assert current_week["status"] == "W"

def test_stats_flow_income_mapping(mock_db_and_config):
    response = client.get("/api/stats/flow")
    assert response.status_code == 200
    data = response.json()
    
    nodes = {node["id"]: node["name"] for node in data["nodes"]}
    income_labels = []
    for link in data["links"]:
        if nodes[link["target"]] == "総収入":
            income_labels.append(nodes[link["source"]])
            
    # Should include mapped labels instead of "MoneyForward"
    assert "Salary" in income_labels
    assert "Investment" in income_labels
    assert "Other Income" in income_labels
    assert "MoneyForward" not in income_labels
