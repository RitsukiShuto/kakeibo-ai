from fastapi import APIRouter, HTTPException, Body
import os
import sqlite3
import pandas as pd
from datetime import date
from src.models import Transaction
from src.api.utils import get_db_path, df_to_json_safe_dict

router = APIRouter(prefix="/api", tags=["reimbursements"])

@router.get("/reimbursements/pending")
async def get_pending_reimbursements():
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = """
        SELECT transaction_date, category, amount, self_amount, (amount - IFNULL(self_amount, 0)) as pending_amount, comment, transaction_id
        FROM transactions 
        WHERE is_reimbursement = 1 AND reimbursement_status != 'completed'
        ORDER BY transaction_date DESC
        """
        df = pd.read_sql_query(query, conn)
        return df_to_json_safe_dict(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.post("/expense-splitter/detect")
def detect_reimbursements():
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM transactions WHERE mode='payment' AND is_reimbursement=0 ORDER BY transaction_date DESC LIMIT 20"
        df_recent = pd.read_sql_query(query, conn)
        if df_recent.empty:
            return []
        from src.analyzer.gemini_analyzer import GeminiAnalyzer
        analyzer = GeminiAnalyzer()
        transactions = [Transaction(
            transaction_id=row['transaction_id'],
            transaction_date=date.fromisoformat(row['transaction_date']),
            category=row['category'],
            amount=row['amount'],
            comment=row['comment'],
            source=row['source'],
            mode=row['mode']
        ) for _, row in df_recent.iterrows()]
        suggestions = analyzer.detect_potential_reimbursements(transactions)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.post("/expense-splitter/parse")
def parse_reimbursement(text: str = Body(..., embed=True), total_amount: int = Body(..., embed=True)):
    try:
        from src.analyzer.gemini_analyzer import KakeiboAnalyzer
        analyzer = KakeiboAnalyzer()
        result = analyzer.parse_reimbursement_text(text, total_amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
