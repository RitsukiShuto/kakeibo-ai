import sqlite3
import json
import os
from datetime import datetime, date
from typing import List, Optional
from src.models import Transaction, Asset
from src.utils.logger import logger

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            local_dir = os.getenv("KAKEIBO_LOCAL_DIR", "local")
            db_path = os.getenv("KAKEIBO_DB_PATH", os.path.join(local_dir, "kakeibo.db"))
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
                self_amount INTEGER,
                is_reimbursement INTEGER DEFAULT 0,
                reimbursement_status TEXT,
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
                model_name TEXT,
                prompt_tokens INTEGER,
                response_tokens INTEGER,
                total_tokens INTEGER,
                raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 既存テーブルへのカラム追加 (移行用)
        try:
            cursor.execute("ALTER TABLE analysis_history ADD COLUMN model_name TEXT")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE analysis_history ADD COLUMN prompt_tokens INTEGER")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE analysis_history ADD COLUMN response_tokens INTEGER")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE analysis_history ADD COLUMN total_tokens INTEGER")
        except sqlite3.OperationalError: pass

        # 4. System Status テーブル (サービス稼働確認用)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_status (
                service_name TEXT PRIMARY KEY,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                INSERT INTO transactions (
                    transaction_id, transaction_date, category, genre, amount, 
                    comment, source, mode, self_amount, is_reimbursement, reimbursement_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    transaction_date=excluded.transaction_date,
                    category=excluded.category,
                    genre=excluded.genre,
                    amount=excluded.amount,
                    comment=excluded.comment,
                    mode=excluded.mode,
                    self_amount=COALESCE(excluded.self_amount, transactions.self_amount),
                    is_reimbursement=MAX(excluded.is_reimbursement, transactions.is_reimbursement),
                    reimbursement_status=COALESCE(excluded.reimbursement_status, transactions.reimbursement_status)
            """, (
                t.transaction_id or f"{t.source}_{t.transaction_date}_{t.amount}_{t.comment}",
                t.transaction_date.isoformat(),
                t.category,
                t.genre,
                t.amount,
                t.comment,
                t.source,
                t.mode,
                t.self_amount,
                t.is_reimbursement,
                t.reimbursement_status
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

    def save_analysis(self, timeframe: str, summary: str, report_path: str, score: int, raw_response: str, 
                      model_name: str = None, prompt_tokens: int = None, response_tokens: int = None, total_tokens: int = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis_history (
                timeframe, summary, report_path, score, raw_response, 
                model_name, prompt_tokens, response_tokens, total_tokens
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timeframe, summary, report_path, score, raw_response, 
              model_name, prompt_tokens, response_tokens, total_tokens))
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
            mode=row["mode"],
            self_amount=row["self_amount"],
            is_reimbursement=row["is_reimbursement"],
            reimbursement_status=row["reimbursement_status"]
        ) for row in rows]
        
        if self.db_path != ":memory:":
            conn.close()
        return result

    def get_transactions_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """
        指定した期間の取引明細を取得
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE transaction_date BETWEEN ? AND ?
            ORDER BY transaction_date ASC
        """, (start_date.isoformat(), end_date.isoformat()))
        rows = cursor.fetchall()
        
        result = [Transaction(
            transaction_id=row["transaction_id"],
            transaction_date=date.fromisoformat(row["transaction_date"]),
            category=row["category"],
            genre=row["genre"],
            amount=row["amount"],
            comment=row["comment"],
            source=row["source"],
            mode=row["mode"],
            self_amount=row["self_amount"],
            is_reimbursement=row["is_reimbursement"],
            reimbursement_status=row["reimbursement_status"]
        ) for row in rows]
        
        if self.db_path != ":memory:":
            conn.close()
        return result

    def get_monthly_actual_income(self, year: int, month: int) -> int:
        """
        指定した年月の合計収入（mode='income'）を取得
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        date_pattern = f"{year}-{month:02d}-%"
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE mode = 'income' AND transaction_date LIKE ?
        """, (date_pattern,))
        result = cursor.fetchone()[0] or 0
        if self.db_path != ":memory:":
            conn.close()
        return result

    def get_monthly_total_assets(self, year: int, month: int) -> int:
        """
        指定した年月の最終的な資産総額を取得（その月の最後の記録日を使用）
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        date_pattern = f"{year}-{month:02d}-%"
        cursor.execute("""
            SELECT SUM(amount) FROM assets 
            WHERE acquired_date IN (
                SELECT MAX(acquired_date) FROM assets 
                WHERE acquired_date LIKE ?
            )
        """, (date_pattern,))
        result = cursor.fetchone()[0] or 0
        if self.db_path != ":memory:":
            conn.close()
        return result

    def get_monthly_balance(self, year: int, month: int) -> dict:
        """
        指定した年月の収入・支出・収支をまとめて取得
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        date_pattern = f"{year}-{month:02d}-%"
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN mode = 'income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN mode = 'payment' THEN amount ELSE 0 END) as expense
            FROM transactions 
            WHERE transaction_date LIKE ?
        """, (date_pattern,))
        row = cursor.fetchone()
        income = row["income"] or 0
        expense = row["expense"] or 0
        
        if self.db_path != ":memory:":
            conn.close()
            
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense
        }

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
        最新日付の全資産情報を取得
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
            SELECT * FROM assets 
            WHERE acquired_date = ?
        """, (latest_date,))
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

    def get_pending_reimbursements(self) -> List[Transaction]:
        """
        未精算の立替明細を取得
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE is_reimbursement = 1 AND reimbursement_status != 'completed'
            ORDER BY transaction_date ASC
        """)
        rows = cursor.fetchall()
        
        result = [Transaction(
            transaction_id=row["transaction_id"],
            transaction_date=date.fromisoformat(row["transaction_date"]),
            category=row["category"],
            genre=row["genre"],
            amount=row["amount"],
            comment=row["comment"],
            source=row["source"],
            mode=row["mode"],
            self_amount=row["self_amount"],
            is_reimbursement=row["is_reimbursement"],
            reimbursement_status=row["reimbursement_status"]
        ) for row in rows]
        
        if self.db_path != ":memory:":
            conn.close()
        return result

    def auto_match_reimbursements(self):
        """
        未精算の立替明細と、新しい入金明細を照合し、自動的に精算完了にする。
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 1. 未精算（pending/partial）の立替明細を取得
        cursor.execute("""
            SELECT transaction_id, transaction_date, amount, self_amount, category
            FROM transactions
            WHERE is_reimbursement = 1 AND reimbursement_status != 'completed' AND mode = 'payment'
        """)
        pending_txs = cursor.fetchall()
        
        if not pending_txs:
            if self.db_path != ":memory:":
                conn.close()
            return []

        matched_count = 0
        for p in pending_txs:
            # 回収すべき金額
            reimbursement_amount = p["amount"] - (p["self_amount"] or 0)
            p_date = p["transaction_date"]
            
            # 2. その立替日以降に、同額の入金（income）があるか探す
            # 多少の日付のズレ（立替から回収までの期間）を考慮し、特に期限は設けない（立替日以降であればOK）
            cursor.execute("""
                SELECT transaction_id, transaction_date, comment
                FROM transactions
                WHERE mode = 'income' AND amount = ? AND transaction_date >= ?
                ORDER BY transaction_date ASC
                LIMIT 1
            """, (reimbursement_amount, p_date))
            
            income_match = cursor.fetchone()
            if income_match:
                # 一致するものが見つかった場合、立替明細を 'completed' に更新
                cursor.execute("""
                    UPDATE transactions 
                    SET reimbursement_status = 'completed' 
                    WHERE transaction_id = ?
                """, (p["transaction_id"],))
                matched_count += 1
                logger.debug(f"Auto-matched reimbursement: {p['category']} ({reimbursement_amount}円) matched with income on {income_match['transaction_date']}")

        conn.commit()
        if self.db_path != ":memory:":
            conn.close()
        return matched_count

    def update_heartbeat(self, service_name: str):
        """
        サービスの生存確認用タイムスタンプを更新 (UTC)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # タイムゾーンの影響を避けるため UTC を使用
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO system_status (service_name, last_heartbeat)
                VALUES (?, ?)
                ON CONFLICT(service_name) DO UPDATE SET last_heartbeat = excluded.last_heartbeat
            """, (service_name, now))
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()
        except Exception as e:
            logger.error(f"Failed to update heartbeat for {service_name}: {e}")

    def get_service_status(self, service_name: str) -> Optional[str]:
        """
        サービスの最終生存確認時刻を取得 (UTC)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT last_heartbeat FROM system_status WHERE service_name = ?", (service_name,))
            row = cursor.fetchone()
            if self.db_path != ":memory:":
                conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Failed to get service status for {service_name}: {e}")
            return None
