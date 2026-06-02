from fastapi import APIRouter, HTTPException, Body
import os
import sqlite3
import pandas as pd
from typing import Optional, List
from pydantic import BaseModel
from src.models import Transaction as TransactionModel
from src.db.database import Database
from src.api.utils import get_db_path, get_config_dir, load_config, df_to_json_safe_dict, ROOT_DIR

router = APIRouter(prefix="/api", tags=["analysis"])

@router.get("/analysis-history")
async def get_analysis_history(timeframe: str = "monthly"):
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM analysis_history WHERE timeframe = ? ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn, params=(timeframe,))
        return df_to_json_safe_dict(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/analysis-history/{history_id}/content")
async def get_analysis_content(history_id: int):
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT report_path FROM analysis_history WHERE id = ?", (history_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Report not found")
        report_path = row[0]
        if report_path.startswith("./"):
            report_path = report_path[2:]
        if not os.path.isabs(report_path):
            report_path = os.path.join(ROOT_DIR, report_path)
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content}
        else:
            raise HTTPException(status_code=404, detail=f"Report file not found at {report_path}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
