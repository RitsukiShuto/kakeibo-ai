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

print(f"📡 API starting using database: {get_db_path()}")

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
            # 旧形式の互換性維持: 各カテゴリを独立した項目として扱う
            if "budget" not in data.get("monthly", {}):
                old_categories = data.get("monthly", {}).get("categories", {})
                if "monthly" not in data: data["monthly"] = {}
                data["monthly"]["budget"] = {"variable": {cat: amt for cat, amt in old_categories.items()}}
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

def df_to_json_safe_dict(df):
    """
    DataFrameをJSON互換の辞書リストに変換する。
    NaNやInfをNone(null)に確実に置換する。
    """
    import numpy as np
    # 一度すべての NaN/Inf を None に変換
    # 浮動小数点列の場合は単純な where では戻ることがあるため、
    # mask を使って明示的にオブジェクト型として None を入れる
    df_safe = df.replace([np.inf, -np.inf], np.nan)
    return [{k: (v if pd.notnull(v) else None) for k, v in record.items()} for record in df_safe.to_dict(orient="records")]

@app.get("/api/status")
async def get_status():
    try:
        db_path = get_db_path()
        db_instance = Database(db_path=db_path)
        
        slack_heartbeat = db_instance.get_service_status("slack")
        slack_online = False
        
        if slack_heartbeat:
            # ハートビートは UTC で記録されている前提
            last_time = datetime.strptime(slack_heartbeat, "%Y-%m-%d %H:%M:%S")
            # 3分以内の更新があればオンラインとみなす
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

@app.get("/api/settings/ai-models")
async def get_ai_models():
    config_dir = get_config_dir()
    settings_path = os.path.join(config_dir, "settings.json")
    example_path = os.path.join(config_dir, "settings.json.example")
    
    if not os.path.exists(settings_path) and os.path.exists(example_path):
        import shutil
        shutil.copy(example_path, settings_path)
        
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            ai_settings = settings.get("ai", {})
            
            personas_dir = "prompts/personas"
            personas = []
            if os.path.exists(personas_dir):
                for file_name in os.listdir(personas_dir):
                    if file_name.endswith(".md"):
                        p_id = file_name.replace(".md", "")
                        name_map = {"gal": "ギャル", "butler": "執事", "zen": "癒やし系", "default": "標準（丁寧）", "sergeant": "軍曹（厳しめ）"}
                        desc_map = {
                            "gal": "絵文字たっぷりでフレンドリーにアドバイスします",
                            "butler": "お嬢様・ご主人様として丁重にお仕えします",
                            "zen": "落ち着いたトーンで心に寄り添いアドバイスします",
                            "default": "標準的で丁寧なアシスタントです",
                            "sergeant": "厳しくスパルタに家計を指導します"
                        }
                        personas.append({
                            "id": p_id,
                            "name": name_map.get(p_id, p_id.title()),
                            "description": desc_map.get(p_id, "AIキャラクター")
                        })
            
            ai_settings["available_personas"] = personas
            if "active_persona" not in ai_settings:
                ai_settings["active_persona"] = "gal"
                
            return ai_settings
    return {"error": "Settings file not found"}

@app.put("/api/settings/active-model")
async def update_active_model(data: dict = Body(...)):
    config_dir = get_config_dir()
    settings_path = os.path.join(config_dir, "settings.json")
    new_model = data.get("active_model")
    
    if not new_model:
        raise HTTPException(status_code=400, detail="active_model is required")
        
    try:
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        
        if "ai" not in settings:
            settings["ai"] = {}
        settings["ai"]["active_model"] = new_model
        
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/settings/active-persona")
async def update_active_persona(data: dict = Body(...)):
    config_dir = get_config_dir()
    settings_path = os.path.join(config_dir, "settings.json")
    new_persona = data.get("active_persona")
    
    if not new_persona:
        raise HTTPException(status_code=400, detail="active_persona is required")
        
    try:
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        
        if "ai" not in settings:
            settings["ai"] = {}
        settings["ai"]["active_persona"] = new_persona
        
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Kakeibo AI API is running"}

@app.get("/api/kpi")
async def get_kpi(timeframe: str = "monthly"):
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        total_budget = sum(budget_categories.values()) if budget_categories else 0
        
        # timeframe に応じた日付フィルタを構築
        now = datetime.now()
        if timeframe == "daily":
            date_pattern = now.strftime("%Y-%m-%d")
        elif timeframe == "weekly":
            # 今週の月曜日から今日まで
            from datetime import timedelta
            monday = now - timedelta(days=now.weekday())
            date_pattern = None  # 範囲指定を使用
        else:  # monthly (default)
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

@app.get("/api/budget-actual")
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

@app.get("/api/transactions")
async def get_transactions(limit: int = 50, offset: int = 0, search: Optional[str] = None):
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        if search:
            # 金額での検索（数値として一致するか、文字列として含まれるか）
            amount_query = ""
            params = [f"%{search}%", f"%{search}%", f"%{search}%"]
            
            try:
                search_val = float(search)
                amount_query = " OR amount = ?"
                params.append(search_val)
            except ValueError:
                pass
                
            query = f"SELECT * FROM transactions WHERE comment LIKE ? OR category LIKE ? OR genre LIKE ?{amount_query} ORDER BY transaction_date DESC LIMIT ? OFFSET ?"
            params.append(limit)
            params.append(offset)
            df = pd.read_sql_query(query, conn, params=params)
        else:
            query = "SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT ? OFFSET ?"
            df = pd.read_sql_query(query, conn, params=(limit, offset))

        return df_to_json_safe_dict(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.get("/api/transactions/categories")
async def get_all_categories():
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        # DBからユニークな大項目・中項目を取得
        query = "SELECT DISTINCT category, genre FROM transactions"
        df = pd.read_sql_query(query, conn)
        
        # 予算設定からも取得
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = []
        if budget:
            for section in ["fixed", "variable"]:
                section_data = budget.get("monthly", {}).get("budget", {}).get(section, {})
                for major, minors in section_data.items():
                    if isinstance(minors, dict):
                        for minor in minors.keys():
                            budget_categories.append({"category": major, "genre": minor})
                    else:
                        budget_categories.append({"category": major, "genre": ""})
        
        # 統合してユニークにする
        db_cats = df.to_dict(orient="records")
        all_cats = db_cats + budget_categories
        
        # 重複削除
        seen = set()
        unique_cats = []
        for c in all_cats:
            k = (c["category"], c["genre"])
            if k not in seen:
                seen.add(k)
                unique_cats.append(c)
        
        return unique_cats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

from pydantic import BaseModel

class TransactionUpdate(BaseModel):
    category: Optional[str] = None
    genre: Optional[str] = None
    comment: Optional[str] = None
    is_reimbursement: Optional[int] = None
    self_amount: Optional[int] = None
    reimbursement_status: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        
        # 1. コンテキスト情報の取得
        conn = sqlite3.connect(db_path)
        # 最近の取引10件
        query_tx = "SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 10"
        df_tx = pd.read_sql_query(query_tx, conn)
        from src.models import Transaction
        from datetime import date
        recent_transactions = [Transaction(
            transaction_id=row['transaction_id'],
            transaction_date=date.fromisoformat(row['transaction_date']),
            category=row['category'],
            genre=row['genre'],
            amount=row['amount'],
            comment=row['comment'],
            source=row['source'],
            mode=row['mode']
        ) for _, row in df_tx.iterrows()]
        
        # 資産状況
        db_instance = Database(db_path=db_path)
        asset_summary = db_instance.get_asset_category_summary()
        
        # プロファイルと予算
        profile = load_config(os.path.join(config_dir, "profile.json"))
        budget = load_config(os.path.join(config_dir, "budget.json"))
        
        # 2. AIによる回答生成
        from src.analyzer.gemini_analyzer import GeminiAnalyzer
        analyzer = GeminiAnalyzer()
        response = analyzer.chat(
            message=request.message,
            history=request.history,
            profile=profile,
            budget=budget,
            assets_summary=asset_summary,
            recent_transactions=recent_transactions
        )
        
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(transaction_id: str, update: TransactionUpdate):
    conn = None
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
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.get("/api/analysis-history")
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

@app.get("/api/analysis-history/{history_id}/content")
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
        # 相対パスをプロジェクトルートからの絶対パスに変換
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

@app.get("/api/reimbursements/pending")
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

@app.get("/api/assets")
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
        return df_to_json_safe_dict(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

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
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM transactions WHERE mode='payment' AND is_reimbursement=0 ORDER BY transaction_date DESC LIMIT 20"
        df_recent = pd.read_sql_query(query, conn)
        
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
    finally:
        if conn:
            conn.close()

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
