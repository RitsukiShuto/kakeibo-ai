from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime
from src.db.database import Database
from src.models import Transaction as TransactionModel
from dotenv import load_dotenv
from typing import Optional, List

load_dotenv("local/.env")

# プロジェクトルートの取得
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

app = FastAPI(title="Kakeibo AI API")

# React(Vite)からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発中は一旦全て許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 環境変数から設定を取得。テスト時はこれらを上書きする。
def get_db_path():
    path = os.getenv("KAKEIBO_DB_PATH", "local/kakeibo.db")
    if not os.path.isabs(path):
        path = os.path.join(ROOT_DIR, path)
    return path

def get_config_dir():
    path = os.getenv("KAKEIBO_CONFIG_DIR", "local/config")
    if not os.path.isabs(path):
        path = os.path.join(ROOT_DIR, path)
    return path

def load_budget(config_dir: str):
    budget_path = os.path.join(config_dir, "budget.json")
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 旧形式の互換性維持
            if "budget" not in data.get("monthly", {}):
                old_categories = data.get("monthly", {}).get("categories", {})
                if "monthly" not in data: data["monthly"] = {}
                data["monthly"]["budget"] = {"variable": {"その他": old_categories}}
            return data
    return None

def get_budget_category_totals(budget):
    totals = {}
    if not budget: return totals
    monthly_budget = budget.get("monthly", {}).get("budget", {})
    for section in ["fixed", "variable"]:
        section_data = monthly_budget.get(section, {})
        for category, subcategories in section_data.items():
            if isinstance(subcategories, dict):
                totals[category] = sum(subcategories.values())
            else:
                totals[category] = subcategories
    return totals

@app.get("/api/status")
async def get_status():
    try:
        db_path = get_db_path()
        db_instance = Database(db_path=db_path)
        
        slack_heartbeat = db_instance.get_service_status("slack")
        slack_online = False
        
        if slack_heartbeat:
            last_time = datetime.strptime(slack_heartbeat, "%Y-%m-%d %H:%M:%S")
            # 3分以内の更新があればオンラインとみなす
            if (datetime.now() - last_time).total_seconds() < 180:
                slack_online = True
        
        return {
            "services": {
                "api": {"status": "online", "last_heartbeat": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                "slack": {
                    "status": "online" if slack_online else "offline",
                    "last_heartbeat": slack_heartbeat
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Kakeibo AI API is running"}

@app.get("/api/kpi")
async def get_kpi():
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        total_budget = sum(budget_categories.values()) if budget_categories else 0
        
        current_month = datetime.now().strftime("%Y-%m")
        conn = sqlite3.connect(db_path)
        query_total = f"SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment'"
        actual_total = pd.read_sql_query(query_total, conn)['total'].iloc[0] or 0
        
        query_assets = "SELECT SUM(amount) as total FROM assets WHERE acquired_date = (SELECT MAX(acquired_date) FROM assets)"
        total_assets = pd.read_sql_query(query_assets, conn)['total'].iloc[0] or 0
        conn.close()
        
        return {
            "budget": total_budget,
            "actual": int(actual_total),
            "remaining": max(0, total_budget - int(actual_total)),
            "total_assets": int(total_assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/budget-actual")
async def get_budget_actual():
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        if not budget_categories:
            return []
            
        current_month = datetime.now().strftime("%Y-%m")
        conn = sqlite3.connect(db_path)
        query = f"SELECT category, SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as actual FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment' GROUP BY category"
        df_actual = pd.read_sql_query(query, conn)
        conn.close()
        
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

@app.get("/api/transactions")
async def get_transactions(limit: int = 50, search: Optional[str] = None):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        if search:
            query = "SELECT * FROM transactions WHERE comment LIKE ? OR category LIKE ? ORDER BY transaction_date DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(f"%{search}%", f"%{search}%", limit))
        else:
            query = "SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        # JSON互換性のためにNaNをNoneに置換
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class TransactionUpdate(BaseModel):
    category: Optional[str] = None
    comment: Optional[str] = None
    is_reimbursement: Optional[int] = None
    self_amount: Optional[int] = None
    reimbursement_status: Optional[str] = None

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(transaction_id: str, update: TransactionUpdate):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        update_data = update.model_dump(exclude_unset=True)
        fields = []
        values = []
        for key, value in update_data.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if not fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
            
        values.append(transaction_id)
        query = f"UPDATE transactions SET {', '.join(fields)} WHERE transaction_id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis-history")
async def get_analysis_history(timeframe: str = "monthly"):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM analysis_history WHERE timeframe = ? ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn, params=(timeframe,))
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis-history/{history_id}/content")
async def get_analysis_content(history_id: int):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT report_path FROM analysis_history WHERE id = ?", (history_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Report not found")
            
        report_path = row[0]
        # `./reports` から始まる相対パスを、プロジェクトルートからのパスに調整
        if report_path.startswith("./"):
            report_path = report_path[2:]
            
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content}
        else:
            raise HTTPException(status_code=404, detail=f"Report file not found at {report_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reimbursements/pending")
async def get_pending_reimbursements():
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
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets")
async def get_assets():
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
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings/budget")
async def get_budget_settings():
    config_dir = get_config_dir()
    budget_path = os.path.join(config_dir, "budget.json")
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Budget file not found"}

@app.put("/api/settings/budget")
async def update_budget_settings(data: dict):
    config_dir = get_config_dir()
    budget_path = os.path.join(config_dir, "budget.json")
    try:
        with open(budget_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings/profile")
async def get_profile_settings():
    config_dir = get_config_dir()
    profile_path = os.path.join(config_dir, "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Profile file not found"}

@app.put("/api/settings/profile")
async def update_profile_settings(data: dict):
    config_dir = get_config_dir()
    profile_path = os.path.join(config_dir, "profile.json")
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expense-splitter/detect")
async def detect_reimbursements():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM transactions WHERE mode='payment' AND is_reimbursement=0 ORDER BY transaction_date DESC LIMIT 20"
        df_recent = pd.read_sql_query(query, conn)
        conn.close()
        
        if df_recent.empty:
            return []
            
        from src.analyzer.gemini_analyzer import GeminiAnalyzer
        from src.models import Transaction
        from datetime import date
        
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

@app.post("/api/expense-splitter/parse")
async def parse_reimbursement(text: str = Body(..., embed=True), total_amount: int = Body(..., embed=True)):
    try:
        from src.analyzer.gemini_analyzer import GeminiAnalyzer
        analyzer = GeminiAnalyzer()
        result = analyzer.parse_reimbursement_text(text, total_amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
