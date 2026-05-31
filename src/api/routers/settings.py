from fastapi import APIRouter, HTTPException, Body
import os
import json
import shutil
import sqlite3
import pandas as pd
from src.api.utils import get_config_dir, load_budget, ROOT_DIR, LOCAL_DIR

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/ai-models")
async def get_ai_models():
    config_dir = get_config_dir()
    settings_path = os.path.join(config_dir, "settings.json")
    example_path = os.path.join(config_dir, "settings.json.example")
    
    if not os.path.exists(settings_path) and os.path.exists(example_path):
        shutil.copy(example_path, settings_path)
        
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            ai_settings = settings.get("ai", {})
            
            personas_dir = os.path.join(ROOT_DIR, "prompts/personas")
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

@router.put("/active-model")
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

@router.put("/active-persona")
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

@router.get("/env")
async def get_env_settings():
    env_keys = [
        "MF_USER_ID", "MF_PASSWORD", 
        "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_USER_ID",
        "GEMINI_API_KEY", "LLM_PROVIDER"
    ]
    
    env_path = os.path.join(ROOT_DIR, LOCAL_DIR, ".env")
    env_data = {}
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key_val = line.strip().split("=", 1)
                    if len(key_val) == 2:
                        key, value = key_val
                        if key in env_keys:
                            if value and len(value) > 8 and key not in ["LLM_PROVIDER", "SLACK_USER_ID"]:
                                env_data[key] = value[:4] + "..." + value[-4:]
                            else:
                                env_data[key] = value
    
    for k in env_keys:
        if k not in env_data:
            env_data[k] = ""
            
    return env_data

@router.put("/env")
async def update_env_settings(data: dict = Body(...)):
    env_path = os.path.join(ROOT_DIR, LOCAL_DIR, ".env")
    current_env = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key_val = line.strip().split("=", 1)
                    if len(key_val) == 2:
                        k, v = key_val
                        current_env[k] = v
    
    for key, value in data.items():
        if "..." in str(value) and key in current_env:
            continue
        current_env[key] = value
        
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in current_env.items():
                f.write(f"{k}={v}\n")
        
        for k, v in current_env.items():
            os.environ[k] = str(v)
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budget")
async def get_budget_settings():
    config_dir = get_config_dir()
    budget_path = os.path.join(config_dir, "budget.json")
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Budget file not found"}

@router.put("/budget")
async def update_budget_settings(data: dict):
    config_dir = get_config_dir()
    budget_path = os.path.join(config_dir, "budget.json")
    try:
        with open(budget_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def get_profile_settings():
    config_dir = get_config_dir()
    profile_path = os.path.join(config_dir, "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Profile file not found"}

@router.put("/profile")
async def update_profile_settings(data: dict):
    config_dir = get_config_dir()
    profile_path = os.path.join(config_dir, "profile.json")
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mapping")
async def get_mapping_settings():
    config_dir = get_config_dir()
    mapping_path = os.path.join(config_dir, "mapping.json")
    if os.path.exists(mapping_path):
        with open(mapping_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"category_mappings": {}, "genre_mappings": {}}

@router.put("/mapping")
async def update_mapping_settings(data: dict):
    config_dir = get_config_dir()
    mapping_path = os.path.join(config_dir, "mapping.json")
    try:
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mapping/suggest")
def suggest_mappings():
    from src.api.utils import get_db_path
    conn = None
    try:
        db_path = get_db_path()
        config_dir = get_config_dir()
        
        budget = load_budget(config_dir)
        if not budget:
            raise HTTPException(status_code=400, detail="Budget not configured")
        
        target_categories = []
        monthly_budget = budget.get("monthly", {}).get("budget", {})
        for section in ["fixed", "variable"]:
            target_categories.extend(monthly_budget.get(section, {}).keys())
        
        mapping_path = os.path.join(config_dir, "mapping.json")
        current_mappings = {"category_mappings": {}, "genre_mappings": {}}
        if os.path.exists(mapping_path):
            with open(mapping_path, "r", encoding="utf-8") as f:
                current_mappings = json.load(f)
        
        conn = sqlite3.connect(db_path)
        query = "SELECT DISTINCT category, genre FROM transactions"
        df = pd.read_sql_query(query, conn)
        
        unmapped_items = []
        for _, row in df.iterrows():
            cat = row['category']
            gen = row['genre']
            
            is_mapped = False
            if cat in current_mappings.get("category_mappings", {}):
                is_mapped = True
            if gen in current_mappings.get("genre_mappings", {}):
                is_mapped = True
            if cat in target_categories:
                is_mapped = True
                
            if not is_mapped:
                unmapped_items.append({"category": cat, "genre": gen})
        
        if not unmapped_items:
            return []
            
        from src.analyzer.gemini_analyzer import KakeiboAnalyzer
        analyzer = KakeiboAnalyzer()
        suggestions = analyzer.suggest_category_mappings(unmapped_items[:20], target_categories)
        
        for s in suggestions:
            raw_cat = s.get("raw_category")
            raw_gen = s.get("raw_genre")
            
            if raw_gen:
                q = "SELECT transaction_date, amount, comment FROM transactions WHERE category = ? AND genre = ? ORDER BY transaction_date DESC LIMIT 3"
                p = (raw_cat, raw_gen)
            else:
                q = "SELECT transaction_date, amount, comment FROM transactions WHERE category = ? AND (genre IS NULL OR genre = '') ORDER BY transaction_date DESC LIMIT 3"
                p = (raw_cat,)
            
            matches = pd.read_sql_query(q, conn, params=p)
            s["examples"] = matches.to_dict(orient="records")
        
        return suggestions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/cron")
async def get_cron_settings():
    config_dir = get_config_dir()
    settings_path = os.path.join(config_dir, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        return settings.get("cron", {"enabled": True, "time": "23:50", "timeframe": "weekly"})
    return {"enabled": True, "time": "23:50", "timeframe": "weekly"}

@router.put("/cron")
async def update_cron_settings(data: dict = Body(...)):
    config_dir = get_config_dir()
    settings_path = os.path.join(config_dir, "settings.json")
    try:
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        settings["cron"] = {
            "enabled": data.get("enabled", True),
            "time": data.get("time", "23:50"),
            "timeframe": data.get("timeframe", "weekly")
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
