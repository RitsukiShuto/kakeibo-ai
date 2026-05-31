from fastapi import APIRouter, HTTPException
import os
import sqlite3
import pandas as pd
from datetime import datetime
from src.db.database import Database
from src.api.utils import get_db_path, get_config_dir, load_budget, get_budget_category_totals

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/status")
async def get_status():
    try:
        db_path = get_db_path()
        db_instance = Database(db_path=db_path)
        
        slack_heartbeat = db_instance.get_service_status("slack")
        slack_online = False
        
        if slack_heartbeat:
            last_time = datetime.strptime(slack_heartbeat, "%Y-%m-%d %H:%M:%S")
            if (datetime.utcnow() - last_time).total_seconds() < 180:
                slack_online = True
        
        return {
            "services": {
                "api": {"status": "online", "last_heartbeat": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")},
                "slack": {
                    "status": "online" if slack_online else "offline",
                    "last_heartbeat": slack_heartbeat
                }
            }
        }
    except Exception as e:
        print(f"Error in get_status: {e}")
        return {
            "services": {
                "api": {"status": "error", "detail": str(e)},
                "slack": {"status": "unknown"}
            }
        }

@router.get("/kpi")
async def get_kpi(timeframe: str = "monthly"):
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        total_budget = sum(budget_categories.values()) if budget_categories else 0
        
        now = datetime.now()
        if timeframe == "daily":
            date_pattern = now.strftime("%Y-%m-%d")
        elif timeframe == "weekly":
            from datetime import timedelta
            monday = now - timedelta(days=now.weekday())
            date_pattern = None
        else:
            date_pattern = now.strftime("%Y-%m")
        
        conn = sqlite3.connect(db_path)
        
        if timeframe == "weekly":
            from datetime import timedelta
            monday = now - timedelta(days=now.weekday())
            query_total = "SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date BETWEEN ? AND ? AND mode='payment'"
            actual_total = pd.read_sql_query(query_total, conn, params=(monday.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")))['total'].iloc[0]
        else:
            query_total = "SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date LIKE ? AND mode='payment'"
            actual_total = pd.read_sql_query(query_total, conn, params=(f"{date_pattern}%",))['total'].iloc[0]
        
        actual_total = int(actual_total) if pd.notnull(actual_total) else 0

        query_assets = "SELECT SUM(amount) as total FROM assets WHERE acquired_date = (SELECT MAX(acquired_date) FROM assets)"
        total_assets = pd.read_sql_query(query_assets, conn)['total'].iloc[0]
        total_assets = int(total_assets) if pd.notnull(total_assets) else 0

        return {
            "budget": total_budget,
            "actual": actual_total,
            "remaining": max(0, total_budget - actual_total),
            "total_assets": total_assets
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/budget-actual")
async def get_budget_actual():
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        if not budget_categories:
            return []
            
        current_month = datetime.now().strftime("%Y-%m")
        conn = sqlite3.connect(db_path)
        query = "SELECT category, SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as actual FROM transactions WHERE transaction_date LIKE ? AND mode='payment' GROUP BY category"
        df_actual = pd.read_sql_query(query, conn, params=(f"{current_month}%",))
        
        result = []
        for cat, b_amt in budget_categories.items():
            actual_row = df_actual[df_actual['category'] == cat]
            a_amt = int(actual_row['actual'].iloc[0]) if not actual_row.empty else 0
            result.append({
                "category": cat,
                "budget": b_amt,
                "actual": a_amt
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/assets")
async def get_assets():
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = """
        SELECT acquired_date, asset_type, SUM(amount) as total_amount
        FROM assets
        GROUP BY acquired_date, asset_type
        ORDER BY acquired_date ASC
        """
        df = pd.read_sql_query(query, conn)
        from src.api.utils import df_to_json_safe_dict
        return df_to_json_safe_dict(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
