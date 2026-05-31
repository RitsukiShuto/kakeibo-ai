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

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None
    model: Optional[str] = None

@router.post("/chat")
def chat(request: ChatRequest):
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        conn = sqlite3.connect(db_path)
        query_tx = "SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 10"
        df_tx = pd.read_sql_query(query_tx, conn)
        from datetime import date
        recent_transactions = []
        for _, row in df_tx.iterrows():
            try:
                d_str = str(row['transaction_date'])
                if '/' in d_str:
                    from datetime import datetime
                    d = datetime.strptime(d_str, "%Y/%m/%d").date()
                else:
                    d = date.fromisoformat(d_str)
                recent_transactions.append(TransactionModel(
                    transaction_id=row['transaction_id'],
                    transaction_date=d,
                    category=row['category'],
                    genre=row['genre'] if 'genre' in row and pd.notnull(row['genre']) else "",
                    amount=row['amount'],
                    comment=row['comment'] if pd.notnull(row['comment']) else "",
                    source=row['source'],
                    mode=row['mode']
                ))
            except Exception as e:
                print(f"Skipping transaction in context due to parse error: {e}")
        db_instance = Database(db_path=db_path)
        asset_summary = db_instance.get_asset_category_summary()
        profile = load_config(os.path.join(config_dir, "profile.json"))
        budget = load_config(os.path.join(config_dir, "budget.json"))
        from src.analyzer.gemini_analyzer import KakeiboAnalyzer
        analyzer = KakeiboAnalyzer()
        response = analyzer.chat(
            message=request.message,
            history=request.history,
            profile=profile,
            budget=budget,
            assets_summary=asset_summary,
            recent_transactions=recent_transactions,
            model_override=request.model
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    finally:
        if conn:
            conn.close()

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

@router.get("/life-plan/simulation")
def get_life_plan_simulation():
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        db_instance = Database(db_path=db_path)
        assets_summary = db_instance.get_asset_category_summary()
        total_assets = sum(a['amount'] for a in assets_summary)
        profile = load_config(os.path.join(config_dir, "profile.json"))
        budget = load_config(os.path.join(config_dir, "budget.json"))
        user_info = profile.get("user", {})
        life_plan = user_info.get("life_plan", {})
        if not life_plan:
            raise HTTPException(status_code=400, detail="Life plan settings not found in profile.json")
        from src.utils.life_plan_calculator import LifePlanCalculator
        monthly_savings = budget.get("monthly", {}).get("savings_goal", 0) + budget.get("monthly", {}).get("investment_goal", 0)
        calculator = LifePlanCalculator(
            current_assets=total_assets,
            monthly_savings=monthly_savings,
            current_age=life_plan.get("current_age", 30),
            retirement_age=life_plan.get("retirement_age", 65),
            annual_return_rate=life_plan.get("annual_return_rate", 3.0),
            annual_inflation_rate=life_plan.get("annual_inflation_rate", 1.0),
            monthly_expenses_post_retirement=life_plan.get("monthly_living_expenses_post_retirement", 200000),
            events=life_plan.get("events", [])
        )
        trajectory = calculator.simulate(end_age=100)
        full_settings = {
            "current_age": life_plan.get("current_age", 30),
            "retirement_age": life_plan.get("retirement_age", 65),
            "annual_return_rate": life_plan.get("annual_return_rate", 3.0),
            "annual_inflation_rate": life_plan.get("annual_inflation_rate", 1.0),
            "monthly_living_expenses_post_retirement": life_plan.get("monthly_living_expenses_post_retirement", 200000),
            "events": life_plan.get("events", []),
            "monthly_savings": monthly_savings
        }
        return {
            "trajectory": trajectory,
            "advice": None,
            "settings": full_settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/life-plan/advice")
def get_life_plan_advice():
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        db_instance = Database(db_path=db_path)
        assets_summary = db_instance.get_asset_category_summary()
        total_assets = sum(a['amount'] for a in assets_summary)
        profile = load_config(os.path.join(config_dir, "profile.json"))
        budget = load_config(os.path.join(config_dir, "budget.json"))
        user_info = profile.get("user", {})
        life_plan = user_info.get("life_plan", {})
        from src.utils.life_plan_calculator import LifePlanCalculator
        monthly_savings = budget.get("monthly", {}).get("savings_goal", 0) + budget.get("monthly", {}).get("investment_goal", 0)
        calculator = LifePlanCalculator(
            current_assets=total_assets,
            monthly_savings=monthly_savings,
            current_age=life_plan.get("current_age", 30),
            retirement_age=life_plan.get("retirement_age", 65),
            annual_return_rate=life_plan.get("annual_return_rate", 3.0),
            annual_inflation_rate=life_plan.get("annual_inflation_rate", 1.0),
            monthly_expenses_post_retirement=life_plan.get("monthly_living_expenses_post_retirement", 200000),
            events=life_plan.get("events", [])
        )
        trajectory = calculator.simulate(end_age=100)
        from src.analyzer.gemini_analyzer import KakeiboAnalyzer
        analyzer = KakeiboAnalyzer()
        advice = analyzer.analyze_life_plan(trajectory, profile, budget)
        return {"advice": advice}
    except Exception as e:
        return {"advice": "アドバイスの生成中にエラーが発生しました。"}
