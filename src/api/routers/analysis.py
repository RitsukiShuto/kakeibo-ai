from fastapi import APIRouter, HTTPException, Body
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
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

@router.get("/analysis-history/latest-summary")
async def get_latest_summary():
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM analysis_history ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return {"summary": "まだ分析データがありません。"}
        return {"summary": row[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/analysis-history/form")
async def get_weekly_form(month: Optional[str] = None):
    """
    指定月、または直近の予算達成状況（勝敗データ）を取得。
    W: 実績 <= 予算, L: 実績 > 予算
    """
    conn = None
    try:
        from src.api.utils import load_budget, get_budget_category_totals
        
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        total_monthly_budget = sum(budget_categories.values()) if budget_categories else 0
        weekly_budget = (total_monthly_budget * 12) / 52
        
        conn = sqlite3.connect(db_path)
        now = datetime.now()
        
        if month:
            try:
                # 指定月の末日を基準にする
                ref_date = datetime.strptime(month, "%Y-%m")
                if ref_date.month == 12:
                    next_month = datetime(ref_date.year + 1, 1, 1)
                else:
                    next_month = datetime(ref_date.year, ref_date.month + 1, 1)
                last_day_of_month = next_month - timedelta(days=1)
                base_date = last_day_of_month
                # 指定月が未来の場合は現在日に制限
                if base_date > now:
                    base_date = now
            except:
                base_date = now
        else:
            base_date = now

        results = []
        
        # 基準日から遡って4週間
        for i in range(3, -1, -1):
            # 週の月曜日を計算
            start_date = base_date - timedelta(days=base_date.weekday() + 7 * i)
            end_date = start_date + timedelta(days=6)
            
            query = "SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date BETWEEN ? AND ? AND mode='payment'"
            actual = pd.read_sql_query(query, conn, params=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))['total'].iloc[0]
            actual = int(actual) if pd.notnull(actual) else 0
            
            # 進行中の週（本日を含む週）かどうかの判定
            is_current_week = start_date <= now <= end_date
            
            if is_current_week:
                # 進行中なので Pace Limit で判定
                days_elapsed = (now - start_date).days + 1
                current_pace_budget = (weekly_budget / 7) * days_elapsed
                status = "W" if actual <= current_pace_budget else "L"
            else:
                status = "W" if actual <= weekly_budget else "L"
            
            results.append({
                "status": status,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            })
                    
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
