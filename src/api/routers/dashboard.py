from fastapi import APIRouter, HTTPException
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
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
async def get_kpi(timeframe: str = "monthly", month: Optional[str] = None):
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        total_budget = sum(budget_categories.values()) if budget_categories else 0
        
        now = datetime.now()
        if month:
            try:
                ref_date = datetime.strptime(month, "%Y-%m")
            except:
                ref_date = now
        else:
            ref_date = now

        if timeframe == "daily":
            date_pattern = ref_date.strftime("%Y-%m-%d")
        elif timeframe == "weekly":
            monday = ref_date - timedelta(days=ref_date.weekday())
            date_pattern = None
        else:
            date_pattern = ref_date.strftime("%Y-%m")
        
        conn = sqlite3.connect(db_path)
        
        if timeframe == "weekly":
            monday = ref_date - timedelta(days=ref_date.weekday())
            sunday = monday + timedelta(days=6)
            query_total = "SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date BETWEEN ? AND ? AND mode='payment'"
            actual_total = pd.read_sql_query(query_total, conn, params=(monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")))['total'].iloc[0]
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
async def get_budget_actual(timeframe: str = "monthly", month: Optional[str] = None, week: Optional[str] = None):
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        budget_categories = get_budget_category_totals(budget)
        if not budget_categories:
            return []
            
        now = datetime.now()
        if month:
            try:
                ref_date = datetime.strptime(month, "%Y-%m")
            except:
                ref_date = now
        else:
            ref_date = now

        # timeframeに応じた期間と予算倍率の設定
        if week and timeframe == "weekly":
            try:
                start_date = datetime.strptime(week, "%Y-%m-%d")
                end_date = start_date + timedelta(days=6)
                days_in_period = 7
                # もし未来の週なら全日経過として扱うか、現在週なら本日まで
                if start_date <= now <= end_date:
                    days_elapsed = (now - start_date).days + 1
                elif now < start_date:
                    days_elapsed = 0
                else:
                    days_elapsed = 7
                multiplier = 7 / 30.44
            except:
                start_date = now - timedelta(days=now.weekday())
                end_date = start_date + timedelta(days=6)
                days_in_period = 7
                days_elapsed = (now - start_date).days + 1
                multiplier = 7 / 30.44
        elif timeframe == "weekly":
            start_date = ref_date - timedelta(days=ref_date.weekday()) # Monday
            end_date = start_date + timedelta(days=6)
            days_in_period = 7
            if start_date <= now <= end_date:
                days_elapsed = (now - start_date).days + 1
            elif now < start_date:
                days_elapsed = 0
            else:
                days_elapsed = 7
            multiplier = 7 / 30.44
        elif timeframe == "quarterly":
            quarter = (ref_date.month - 1) // 3 + 1
            start_date = datetime(ref_date.year, 3 * quarter - 2, 1)
            if quarter == 4:
                end_date = datetime(ref_date.year, 12, 31)
            else:
                end_date = datetime(ref_date.year, 3 * quarter + 1, 1) - timedelta(days=1)
            days_in_period = (end_date - start_date).days + 1
            if start_date <= now <= end_date:
                days_elapsed = (now - start_date).days + 1
            elif now < start_date:
                days_elapsed = 0
            else:
                days_elapsed = days_in_period
            multiplier = 3.0
        elif timeframe == "yearly":
            start_date = datetime(ref_date.year, 1, 1)
            end_date = datetime(ref_date.year, 12, 31)
            days_in_period = 365 if ref_date.year % 4 != 0 else 366
            if start_date <= now <= end_date:
                days_elapsed = (now - start_date).days + 1
            elif now < start_date:
                days_elapsed = 0
            else:
                days_elapsed = days_in_period
            multiplier = 12.0
        else: # monthly
            start_date = datetime(ref_date.year, ref_date.month, 1)
            if ref_date.month == 12:
                end_date = datetime(ref_date.year, 12, 31)
            else:
                end_date = datetime(ref_date.year, ref_date.month + 1, 1) - timedelta(days=1)
            days_in_period = (end_date - start_date).days + 1
            if start_date <= now <= end_date:
                days_elapsed = now.day
            elif now < start_date:
                days_elapsed = 0
            else:
                days_elapsed = days_in_period
            multiplier = 1.0

        conn = sqlite3.connect(db_path)
        query = "SELECT category, SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as actual FROM transactions WHERE transaction_date BETWEEN ? AND ? AND mode='payment' GROUP BY category"
        df_actual = pd.read_sql_query(query, conn, params=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        # 予算設定からセクション情報を取得
        monthly_budget_config = budget.get("monthly", {}).get("budget", {}) if budget else {}
        cat_to_section = {}
        for section in ["fixed", "variable"]:
            for cat in monthly_budget_config.get(section, {}).keys():
                cat_to_section[cat] = section

        result = []
        for cat, b_amt in budget_categories.items():
            actual_row = df_actual[df_actual['category'] == cat]
            a_amt = int(actual_row['actual'].iloc[0]) if not actual_row.empty else 0
            
            # 期間に応じた予算額の計算
            adjusted_budget = int(b_amt * multiplier)
            # Pace Limit (理想的な進捗ライン) の計算
            pace_limit = int((adjusted_budget / days_in_period) * days_elapsed) if days_in_period > 0 else 0
            
            result.append({
                "category": cat,
                "section": cat_to_section.get(cat, "variable"),
                "budget": adjusted_budget,
                "actual": a_amt,
                "pace_limit": pace_limit
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/stats/flow")
async def get_stats_flow(month: Optional[str] = None):
    """
    Sankey Diagram用の多階層フローデータを生成。
    収入源 → 総収入 → カテゴリ(固定/変動) → 詳細カテゴリ
    """
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        budget = load_budget(config_dir)
        
        current_month = month if month else datetime.now().strftime("%Y-%m")
        conn = sqlite3.connect(db_path)
        
        # 1. 収入源の取得 (Moneyforwardなどのアグリゲーターを特定ラベルにマッピングするため、category/genreも取得)
        query_income = "SELECT source, category, genre, SUM(amount) as amount FROM transactions WHERE transaction_date LIKE ? AND mode='income' GROUP BY source, category, genre"
        df_income = pd.read_sql_query(query_income, conn, params=(f"{current_month}%",))
        
        # 2. 支出カテゴリ（実績）の取得
        query_expense = "SELECT category, SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as amount FROM transactions WHERE transaction_date LIKE ? AND mode='payment' GROUP BY category"
        df_expense = pd.read_sql_query(query_expense, conn, params=(f"{current_month}%",))
        
        # Nodes と Links の構築
        nodes = []
        links = []
        node_map = {}

        def add_node(name):
            if name not in node_map:
                node_map[name] = len(nodes)
                nodes.append({"id": node_map[name], "name": name})
            return node_map[name]

        total_income_node = add_node("総収入")
        fixed_node = add_node("固定費")
        variable_node = add_node("変動費")

        # 収入源 → 総収入
        total_income_val = 0
        income_mapped_totals = {} # 複数行が同じラベルにマップされる場合のため集計用
        
        for _, row in df_income.iterrows():
            source_name = row['source']
            # Moneyforwardなどの汎用アグリゲーターの場合、内容に基づいてラベルを付与
            if source_name in ["MoneyForward", "マネーフォワード", "Moneyforward"]:
                category = row['category'] or ""
                genre = row['genre'] or ""
                if genre == '給与' or category == '給与':
                    label = "Salary"
                elif '配当' in genre or '配当' in category:
                    label = "Investment"
                elif any(x in genre or x in category for x in ['貯金', '資産', '振替']):
                    label = "Savings"
                else:
                    label = "Other Income"
            else:
                label = source_name
            
            income_mapped_totals[label] = income_mapped_totals.get(label, 0) + int(row['amount'])
            total_income_val += int(row['amount'])

        for label, amount in income_mapped_totals.items():
            src_node = add_node(label)
            links.append({"source": src_node, "target": total_income_node, "value": amount})

        # 予算設定から固定/変動の分類を取得
        monthly_budget = budget.get("monthly", {}).get("budget", {}) if budget else {}
        fixed_cats = monthly_budget.get("fixed", {}).keys()
        variable_cats = monthly_budget.get("variable", {}).keys()

        total_fixed = 0
        total_variable = 0
        
        for _, row in df_expense.iterrows():
            cat = row['category']
            amt = int(row['amount'])
            cat_node = add_node(cat)
            
            if cat in fixed_cats:
                links.append({"source": fixed_node, "target": cat_node, "value": amt})
                total_fixed += amt
            else:
                links.append({"source": variable_node, "target": cat_node, "value": amt})
                total_variable += amt

        # 総収入 → 固定費/変動費
        if total_fixed > 0:
            links.append({"source": total_income_node, "target": fixed_node, "value": total_fixed})
        if total_variable > 0:
            links.append({"source": total_income_node, "target": variable_node, "value": total_variable})

        # 余剰（貯蓄）
        savings = total_income_val - (total_fixed + total_variable)
        if savings > 0:
            savings_node = add_node("貯蓄")
            links.append({"source": total_income_node, "target": savings_node, "value": savings})

        return {"nodes": nodes, "links": links}

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
