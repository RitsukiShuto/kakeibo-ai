import sys
import os
import argparse
import requests
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# プロジェクトのルートをパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher
from src.db.database import Database

def fetch_history_fast(months: int, headless: bool):
    print(f"=== マネーフォワード 高速・一括データ取得 ({months}ヶ月分) ===")
    
    fetcher = MoneyForwardFetcher()
    db = Database()
    
    # 1. ブラウザからCookieを抜いてくる (これに10〜20秒かかる)
    print("ブラウザからログイン情報を抽出中...")
    cookies = fetcher.get_session_cookies(headless=headless)
    
    if not cookies:
        print("エラー: Cookieの取得に失敗しました。ログイン状態を確認してください。")
        return

    session = requests.Session()
    session.cookies.update(cookies)
    
    current_date = date.today()
    total_imported = 0
    csv_dir = os.path.join(os.getcwd(), "data", "csv")
    os.makedirs(csv_dir, exist_ok=True)

    # 2. HTTPリクエストで爆速ダウンロード
    for i in range(months):
        target_date = current_date - relativedelta(months=i)
        year = target_date.year
        month = target_date.month
        
        print(f"[{i+1}/{months}] {year}年{month}月のデータをダウンロード中...", end="", flush=True)
        
        csv_url = f"https://moneyforward.com/cf/csv?month={month}&year={year}"
        
        try:
            response = session.get(csv_url, timeout=30)
            if response.status_code == 200 and len(response.content) > 100:
                # ファイルに一時保存
                csv_path = os.path.join(csv_dir, f"fast_mf_{year}{month:02d}.csv")
                with open(csv_path, "wb") as f:
                    f.write(response.content)
                
                # パースしてDBへ
                transactions = fetcher._parse_csv(csv_path)
                if transactions:
                    db.save_transactions(transactions)
                    print(f" OK! ({len(transactions)}件)")
                    total_imported += len(transactions)
                else:
                    print(" データなし")
            else:
                print(f" 失敗 (HTTP {response.status_code})")
        except Exception as e:
            print(f" エラー: {e}")
        
        # 連続リクエストによるBAN防止 (HTTPリクエストのみなら0.5〜1秒で十分)
        import time
        time.sleep(1)

    print(f"\n=== 高速一括取得完了！ 合計 {total_imported} 件の明細をインポートしました。 ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-speed historical data fetcher")
    parser.add_argument("--months", type=int, default=12, help="遡る月数")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="ブラウザを表示して実行")
    parser.set_defaults(headless=True)
    
    args = parser.parse_args()
    fetch_history_fast(args.months, args.headless)
