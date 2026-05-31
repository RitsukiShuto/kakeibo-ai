import os
import json
import pandas as pd
from dotenv import load_dotenv

# プロジェクトルートの取得
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# ベースディレクトリの設定
LOCAL_DIR = os.getenv("KAKEIBO_LOCAL_DIR", "local")

def get_db_path():
    path = os.getenv("KAKEIBO_DB_PATH", os.path.join(LOCAL_DIR, "kakeibo.db"))
    if not os.path.isabs(path):
        path = os.path.join(ROOT_DIR, path)
    return path

def get_config_dir():
    path = os.getenv("KAKEIBO_CONFIG_DIR", os.path.join(LOCAL_DIR, "config"))
    if not os.path.isabs(path):
        path = os.path.join(ROOT_DIR, path)
    return path

def load_config(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

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
    df_safe = df.replace([np.inf, -np.inf], np.nan)
    return [{k: (v if pd.notnull(v) else None) for k, v in record.items()} for record in df_safe.to_dict(orient="records")]
