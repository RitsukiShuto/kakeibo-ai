import sqlite3
import json
import os
from datetime import datetime, date
from typing import List, Optional
from src.models import Transaction, Asset

class Database:
    def __init__(self, db_path: str = "data/kakeibo.db"):
        self.db_path = db_path
        self._memory_conn = None
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _get_connection(self):
        if self.db_path == ":memory:":
            if self._memory_conn is None:
                self._memory_conn = sqlite3.connect(self.db_path)
                self._memory_conn.row_factory = sqlite3.Row
            return self._memory_conn
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """
        テーブルの作成
        """
        # インメモリの場合は _memory_conn を初期化するために一度呼ぶ
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 1. Transactions テーブル
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Assets テーブル (acquired_date, institution, source の組み合わせで一意にする)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acquired_date TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                source TEXT NOT NULL,
                institution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(acquired_date, institution, source)
            )
        """)
        
        # 3. Analysis History テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timeframe TEXT NOT NULL,
                summary TEXT,
                report_path TEXT,
                score INTEGER,
                raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        if self.db_path != ":memory:":
            conn.close()

    def save_transactions(self, transactions: List[Transaction]):
        """
        明細データを保存（UPSERT）
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        for t in transactions:
            cursor.execute("""
                INSERT INTO transactions (transaction_id, transaction_date, category, genre, amount, comment, source, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    transaction_date=excluded.transaction_date,
                    category=excluded.category,
                    genre=excluded.genre,
                    amount=excluded.amount,
                    comment=excluded.comment,
                    mode=excluded.mode
            """, (
                t.transaction_id or f"{t.source}_{t.transaction_date}_{t.amount}_{t.comment}",
                t.transaction_date.isoformat(),
                t.category,
                t.genre,
                t.amount,
                t.comment,
                t.source,
                t.mode
            ))
        conn.commit()
        if self.db_path != ":memory:":
            conn.close()

    def save_assets(self, assets: List[Asset]):
        """
        資産データを保存（同日のデータがあれば上書き）
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        for a in assets:
            cursor.execute("""
                INSERT INTO assets (acquired_date, asset_type, amount, source, institution)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(acquired_date, institution, source) DO UPDATE SET
                    amount=excluded.amount,
                    asset_type=excluded.asset_type
            """, (
                a.acquired_date.isoformat(),
                a.asset_type,
                a.amount,
                a.source,
                a.institution
            ))
        conn.commit()
        if self.db_path != ":memory:":
            conn.close()

    def get_latest_analysis(self, timeframe: str) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis_history 
            WHERE timeframe = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (timeframe,))
        row = cursor.fetchone()
        result = dict(row) if row else None
        if self.db_path != ":memory:":
            conn.close()
        return result

    def save_analysis(self, timeframe: str, summary: str, report_path: str, score: int, raw_response: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis_history (timeframe, summary, report_path, score, raw_response)
            VALUES (?, ?, ?, ?, ?)
        """, (timeframe, summary, report_path, score, raw_response))
        conn.commit()
        if self.db_path != ":memory:":
            conn.close()

    def get_new_transactions_since_last_analysis(self, timeframe: str) -> List[Transaction]:
        latest = self.get_latest_analysis(timeframe)
        last_created_at = latest["created_at"] if latest else "1970-01-01 00:00:00"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE created_at > ?
        """, (last_created_at,))
        rows = cursor.fetchall()
        
        result = [Transaction(
            transaction_id=row["transaction_id"],
            transaction_date=date.fromisoformat(row["transaction_date"]),
            category=row["category"],
            genre=row["genre"],
            amount=row["amount"],
            comment=row["comment"],
            source=row["source"],
            mode=row["mode"]
        ) for row in rows]
        
        if self.db_path != ":memory:":
            conn.close()
        return result

    def get_asset_category_summary(self) -> List[dict]:
        """
        最新日付の資産情報をカテゴリ別に集計して取得
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(acquired_date) FROM assets")
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            if self.db_path != ":memory:":
                conn.close()
            return []
            
        cursor.execute("""
            SELECT asset_type, SUM(amount) as total_amount
            FROM assets 
            WHERE acquired_date = ?
            GROUP BY asset_type
        """, (latest_date,))
        rows = cursor.fetchall()
        result = [{"category": row["asset_type"], "amount": row["total_amount"]} for row in rows]
        
        if self.db_path != ":memory:":
            conn.close()
        return result

    def get_current_asset_summary(self) -> List[Asset]:
        """
        最新日付の資産情報を取得
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(acquired_date) FROM assets")
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            if self.db_path != ":memory:":
                conn.close()
            return []
            
        cursor.execute("SELECT * FROM assets WHERE acquired_date = ?", (latest_date,))
        rows = cursor.fetchall()
        result = [Asset(
            acquired_date=date.fromisoformat(row["acquired_date"]),
            asset_type=row["asset_type"],
            amount=row["amount"],
            source=row["source"],
            institution=row["institution"]
        ) for row in rows]
        
        if self.db_path != ":memory:":
            conn.close()
        return result
