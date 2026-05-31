from fastapi import APIRouter, HTTPException, UploadFile, File, Body
import os
import sqlite3
import pandas as pd
from typing import Optional, List
from pydantic import BaseModel
from src.models import Transaction as TransactionModel
from src.api.utils import get_db_path, get_config_dir, load_budget, df_to_json_safe_dict

router = APIRouter(prefix="/api", tags=["transactions"])

class TransactionUpdate(BaseModel):
    category: Optional[str] = None
    genre: Optional[str] = None
    comment: Optional[str] = None
    is_reimbursement: Optional[int] = None
    self_amount: Optional[int] = None
    reimbursement_status: Optional[str] = None

@router.get("/transactions")
async def get_transactions(limit: int = 50, offset: int = 0, search: Optional[str] = None):
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        if search:
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

@router.post("/transactions")
async def create_transaction(transaction: TransactionModel):
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if not transaction.transaction_id:
            import uuid
            transaction.transaction_id = str(uuid.uuid4())
        query = """
        INSERT INTO transactions (
            transaction_id, transaction_date, category, genre, amount, 
            comment, source, mode, self_amount, is_reimbursement, reimbursement_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            transaction.transaction_id,
            transaction.transaction_date.isoformat(),
            transaction.category,
            transaction.genre,
            transaction.amount,
            transaction.comment,
            transaction.source,
            transaction.mode,
            transaction.self_amount,
            transaction.is_reimbursement,
            transaction.reimbursement_status
        ))
        conn.commit()
        return {"status": "success", "transaction_id": transaction.transaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.put("/transactions/{transaction_id}")
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

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        conn.commit()
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/transactions/categories")
async def get_all_categories():
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        query = "SELECT DISTINCT category, genre FROM transactions"
        df = pd.read_sql_query(query, conn)
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
        db_cats = df.to_dict(orient="records")
        all_cats = db_cats + budget_categories
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

@router.post("/import/csv")
async def import_transactions_csv(files: list[UploadFile] = File(...)):
    results = []
    total_imported = 0
    errors = []
    from tools.import_data.import_mf_csv import _process_single_csv
    db_path = get_db_path()
    for file in files:
        if not file.filename.endswith('.csv'):
            errors.append({"file": file.filename, "status": "skipped", "reason": "Not a CSV file"})
            continue
        try:
            temp_path = f"data/import/{file.filename}"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as buffer:
                import shutil
                shutil.copyfileobj(file.file, buffer)
            imported_count = _process_single_csv(temp_path, db_path)
            total_imported += imported_count
            results.append({"file": file.filename, "status": "success", "imported": imported_count})
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            errors.append({"file": file.filename, "status": "error", "reason": str(e)})
    return {
        "status": "success" if not errors else "partial_success",
        "total_files": len(files),
        "total_imported": total_imported,
        "details": results + errors
    }
