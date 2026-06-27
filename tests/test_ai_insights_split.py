"""
AI Insights の Summary/Body 分割機能のテスト。
TDD: このテストを先に書き、実装前は全て FAIL することを確認する。
"""
import pytest
import sqlite3
import os
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


@pytest.fixture
def db_with_insights(tmp_path):
    """summary と body の両方を持つ analysis_history を持つ DB"""
    db_path = tmp_path / "test_kakeibo.db"
    os.environ["KAKEIBO_DB_PATH"] = str(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
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
    cursor.execute(
        "INSERT INTO analysis_history (timeframe, summary, body, report_path, score, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "monthly",
            "今月は順調！節約ペース良好🎉",
            "食費は先月比10%減。外食を控え自炊を増やしたことが主因です。来月は交通費に注意しましょう。",
            "reports/test.md",
            80,
            "2026-06-01 12:00:00",
        ),
    )
    conn.commit()
    conn.close()

    yield db_path
    os.environ.pop("KAKEIBO_DB_PATH", None)


@pytest.fixture
def db_empty(tmp_path):
    """レコードなしの DB"""
    db_path = tmp_path / "empty_kakeibo.db"
    os.environ["KAKEIBO_DB_PATH"] = str(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

    yield db_path
    os.environ.pop("KAKEIBO_DB_PATH", None)


# ---------- モデルテスト ----------

class TestAIResponseModel:
    def test_ai_response_has_summary_field(self):
        """AIResponse モデルに summary フィールドがあること"""
        from src.models import AIResponse
        fields = AIResponse.model_fields
        assert "summary" in fields, "AIResponse に summary フィールドがない"

    def test_ai_response_has_body_field(self):
        """AIResponse モデルに body フィールドがあること"""
        from src.models import AIResponse
        fields = AIResponse.model_fields
        assert "body" in fields, "AIResponse に body フィールドがない"

    def test_ai_response_instantiation_with_summary_and_body(self):
        """summary と body を含む AIResponse を正常に生成できること"""
        from src.models import AIResponse
        response = AIResponse(
            summary="今月は順調！",
            body="詳細な分析内容です。食費は適正範囲内でした。",
            slack_report="Slackレポート",
            obsidian_report="Obsidianレポート",
            actions=[],
            asset_breakdown=[],
            budget_status=[],
            totonoi_score=80,
            savings_potential=5000,
        )
        assert response.summary == "今月は順調！"
        assert response.body == "詳細な分析内容です。食費は適正範囲内でした。"


# ---------- DB テスト ----------

class TestDatabaseSaveAnalysis:
    def test_save_analysis_stores_body(self, tmp_path):
        """save_analysis が body を DB に保存できること"""
        from src.db.database import Database
        db_path = str(tmp_path / "test.db")
        db = Database(db_path)

        db.save_analysis(
            timeframe="monthly",
            summary="今月は順調！",
            body="食費は先月比10%減。",
            report_path="",
            score=80,
            raw_response="{}",
        )

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT summary, body FROM analysis_history ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "今月は順調！"
        assert row[1] == "食費は先月比10%減。"


# ---------- API テスト ----------

class TestLatestSummaryEndpoint:
    def test_returns_summary_and_body(self, db_with_insights):
        """summary と body の両方を返すこと"""
        response = client.get("/api/analysis-history/latest-summary")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "body" in data
        assert data["summary"] == "今月は順調！節約ペース良好🎉"
        assert "食費" in data["body"]

    def test_returns_fallback_when_no_data(self, db_empty):
        """データなし時にフォールバックメッセージを返すこと"""
        response = client.get("/api/analysis-history/latest-summary")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "body" in data
        assert data["summary"] != ""
        assert data["body"] != ""
