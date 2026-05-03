import sys
import os
import argparse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from playwright.sync_api import sync_playwright

# プロジェクトのルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher
from src.db.database import Database

def fetch_history(months: int, headless: bool):
    print(f"=== マネーフォワード 過去データ一括取得 ({months}ヶ月分) ===")
    
    fetcher = MoneyForwardFetcher()
    db = Database()
    current_date = date.today()
    total_imported = 0

    with sync_playwright() as p:
        # ブラウザを一度だけ起動
        browser_context = fetcher._launch_browser(p, headless)
        page = browser_context.pages[0]
        
        print("ログイン状態を確認中...")
        if not fetcher._login_and_update(page, headless):
            print("エラー: ログインまたは更新に失敗しました。")
            browser_context.close()
            return

        for i in range(months):
            target_date = current_date - relativedelta(months=i)
            year = target_date.year
            month = target_date.month
            
            print(f"\n[{i+1}/{months}] {year}年{month}月のデータを取得中...")
            
            try:
                # 既存のページを渡して高速・確実に取得
                transactions = fetcher.fetch_historical_transactions(year, month, headless=headless, page=page)
                if transactions:
                    db.save_transactions(transactions)
                    print(f"成功: {len(transactions)}件の明細を保存しました。")
                    total_imported += len(transactions)
                else:
                    print(f"スキップ: {year}年{month}月のデータが見つからないか、取得に失敗しました。")
            except Exception as e:
                print(f"エラー発生 ({year}/{month}): {e}")
            
            # 連続リクエストによる負荷軽減（直接ダウンロードURLなので少し短縮可能）
            if i < months - 1:
                wait_time = 3
                print(f"待機中 ({wait_time}秒)...")
                import time
                time.sleep(wait_time)

        browser_context.close()

    print(f"\n=== 一括取得完了！ 合計 {total_imported} 件の明細をインポートしました。 ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk fetch historical data from MoneyForward")
    parser.add_argument("--months", type=int, default=12, help="遡る月数 (デフォルト: 12)")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="ブラウザを表示して実行")
    parser.set_defaults(headless=True)
    
    args = parser.parse_args()
    fetch_history(args.months, args.headless)
