import os
import json
import time
from datetime import datetime
from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = "config/settings.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"is_setup_completed": False}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def main():
    print("=== マネーフォワード データ取得フェーズ ===")
    
    # 設定の読み込み
    config = load_config()
    is_setup = not config.get("is_setup_completed", False)
    
    if is_setup:
        print("[SETUP MODE] ブラウザを表示して実行します。初回ログインと2段階認証を完了させてください。")
    else:
        print("[NORMAL MODE] バックグラウンドで実行します。")

    # ログイン情報の確認
    user_id = os.getenv("MF_USER_ID")
    password = os.getenv("MF_PASSWORD")
    
    if not user_id or not password:
        print("エラー: .env ファイルに MF_USER_ID と MF_PASSWORD を設定してください。")
        return

    fetcher = MoneyForwardFetcher()
    
    try:
        # 設定に基づいて headless モードを切り替え
        data = fetcher.fetch_data(headless=not is_setup)
        
        if data:
            # データの保存
            output = {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "MoneyForward",
                "transactions": data
            }
            output_file = "input_data.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=4, ensure_ascii=False)
                
            print(f"\n成功: {len(data)} 件のデータを '{output_file}' に保存しました。")
            
            # セットアップ未完了だった場合に完了フラグを立てて保存
            if is_setup:
                config["is_setup_completed"] = True
                save_config(config)
                print("--- セットアップが完了しました。次回からは自動実行されます。 ---")
        else:
            print("データが取得できませんでした。")

    except Exception as e:
        print(f"実行中にエラーが発生しました: {e}")
        if is_setup:
            print("セットアップに失敗しました。再度実行してください。")

if __name__ == "__main__":
    main()
