import os
import sys
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# プロジェクトルートをインポートパスに追加
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

local_dir_name = os.getenv("KAKEIBO_LOCAL_DIR", "local")
load_dotenv(os.path.join(ROOT_DIR, f"{local_dir_name}/.env"))

def setup_session():
    """
    MoneyForwardの初期ログインを行い、セッションを保存するためのツール
    """
    local_dir_name = os.getenv("KAKEIBO_LOCAL_DIR", "local")
    user_data_dir = os.path.join(ROOT_DIR, f"{local_dir_name}/mf_session")
    os.makedirs(user_data_dir, exist_ok=True)

    print("--- MoneyForward セッションセットアップ ---")
    print(f"セッション保存先: {user_data_dir}")
    print("ブラウザを起動します。手動でログインを完了させてください。")
    print("ログインが完了し、ホーム画面（家計簿画面）が表示されたら、このターミナルに戻って Enter を押してください。")
    print("------------------------------------------")

    with sync_playwright() as p:
        # 永続的なコンテキストを起動（ヘッドフルモード）
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            slow_mo=500,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.new_page()
        page.goto("https://moneyforward.com/users/sign_in")
        
        input("\nログインが完了したら Enter を押して終了してください...")
        
        print("セッションを保存して終了します。")
        context.close()

def main():
    setup_session()

if __name__ == "__main__":
    main()
