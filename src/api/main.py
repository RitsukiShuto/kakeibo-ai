from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from src.api.utils import ROOT_DIR, LOCAL_DIR, get_db_path
from src.api.routers import dashboard, transactions, settings, analysis, reimbursements

# 環境変数の読み込み
load_dotenv(os.path.join(ROOT_DIR, LOCAL_DIR, ".env"))

app = FastAPI(title="Kakeibo AI API")

# React(Vite)からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発中は一旦全て許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(dashboard)
app.include_router(transactions)
app.include_router(settings)
app.include_router(analysis)
app.include_router(reimbursements)

@app.get("/")
async def root():
    return {"message": "Kakeibo AI API is running"}

print(f"📡 API starting using database: {get_db_path()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
