import argparse
import sys
import json
import os
import io
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def setup_windows_encoding():
    # Windowsでの文字化け対策
    if sys.platform == "win32":
        import io
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.db.database import Database
from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher
from src.fetcher.zaim_fetcher import ZaimFetcher
from src.analyzer.gemini_analyzer import GeminiAnalyzer
from src.output.slack_notifier import SlackNotifier
from src.output.obsidian_writer import ObsidianWriter
from src.output.visualizer import Visualizer

from dotenv import load_dotenv
load_dotenv("local/.env")

def load_config(file_path):
    config_dir = os.getenv("KAKEIBO_CONFIG_DIR", "local/config")
    # もし引数が local/config を含むパスなら、config_dir で置換
    if file_path.startswith("local/config/"):
        file_path = os.path.join(config_dir, os.path.basename(file_path))
        
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_scheduled_timeframes(schedule):
    """
    スケジュール設定に基づき、今日実行すべきタイムフレームのリストを返す
    優先度順に並べる（dailyを最初にするか最後にするかは検討の余地があるが、
    まずは全て実行されることを保証する）
    """
    today = datetime.now()
    weekday = today.strftime("%A") # Monday, Tuesday, ...
    day = today.day
    month = today.month

    reports = schedule.get("reports", {})
    matched_timeframes = []
    
    # daily を最初に追加（毎日実行されるべきもの）
    if reports.get("daily", {}).get("enabled"):
        matched_timeframes.append("daily")

    if reports.get("weekly", {}).get("enabled") and weekday == reports["weekly"].get("target_day", "Monday"):
        matched_timeframes.append("weekly")

    if reports.get("monthly", {}).get("enabled") and day == reports["monthly"].get("target_day", 1):
        matched_timeframes.append("monthly")

    if reports.get("quarterly", {}).get("enabled") and month in reports["quarterly"].get("months", []) and day == 1:
        matched_timeframes.append("quarterly")

    if reports.get("yearly", {}).get("enabled") and month == reports["yearly"].get("month") and day == 1:
        matched_timeframes.append("yearly")
    
    return matched_timeframes

def run_review(timeframe: str, source: str = "mf", headless: bool = True, skip_fetch: bool = False, db_path: str = "local/kakeibo.db", output_slack: bool = True, output_obsidian: bool = True, output_console: bool = True, progress_callback=None):
    """
    家計簿レビューのメイン工程を実行する
    """
    if not timeframe:
        raise ValueError("timeframe must be specified.")

    schedule = load_config("local/config/schedule.json")
    profile = load_config("local/config/profile.json")
    budget = load_config("local/config/budget.json")

    db = Database(db_path=db_path)
    fetcher = MoneyForwardFetcher() if source == "mf" else ZaimFetcher()

    try:
        if not skip_fetch:
            if progress_callback: progress_callback("🔄 データ取得中...（少し時間がかかります）")
            print(f"Fetching transactions from {source}...")
            transactions = fetcher.fetch_transactions(headless=headless)
            if transactions:
                db.save_transactions(transactions)
            
            print(f"Fetching assets from {source}...")
            assets = fetcher.fetch_assets(headless=headless)
            if assets:
                db.save_assets(assets)
            
            # 立替金の自動マッチングを実行
            print("Auto-matching reimbursements...")
            matched = db.auto_match_reimbursements()
            if matched:
                print(f"Successfully auto-matched {matched} reimbursements!")
        
        if progress_callback: progress_callback(f"🧠 {timeframe}の家計簿をAIが分析中...💅✨")
        print(f"Starting AI Analysis ({timeframe})...")
        analyzer = GeminiAnalyzer()
        
        now = datetime.now()
        actual_monthly_income = db.get_monthly_actual_income(now.year, now.month)
        
        # 過去比較データの準備
        comparison_data = {}
        prev_date = now - relativedelta(months=1)
        comparison_data["prev_total_assets"] = db.get_monthly_total_assets(prev_date.year, prev_date.month)
        
        # 収支実績の比較
        prev_bal_info = db.get_monthly_balance(prev_date.year, prev_date.month)
        comparison_data["prev_balance"] = prev_bal_info["balance"]
        
        if timeframe == "daily":
            # 今月の1日から今日までの明細を取得
            start_of_month = now.replace(day=1).date()
            today = now.date()
            new_transactions = db.get_transactions_range(start_of_month, today)
        else:
            new_transactions = db.get_new_transactions_since_last_analysis(timeframe)
            
        asset_summary = db.get_asset_category_summary()
        latest_analysis = db.get_latest_analysis(timeframe)
        previous_summary = latest_analysis["summary"] if latest_analysis else None
        pending_reimbursements = db.get_pending_reimbursements()
        
        ai_response = analyzer.analyze_kakeibo(
            data=new_transactions, 
            assets_summary=asset_summary,
            timeframe=timeframe,
            profile=profile,
            budget=budget,
            previous_summary=previous_summary,
            actual_monthly_income=actual_monthly_income,
            comparison_data=comparison_data,
            pending_reimbursements=pending_reimbursements
        )

        if not ai_response:
            return None

        # 0. グラフの生成
        graph_path = ""
        try:
            visualizer = Visualizer()
            graph_path = visualizer.generate_asset_trend_graph(db_path=db_path)
        except Exception as e:
            print(f"Graph generation failed: {e}")

        # 1. コンソール出力
        if output_console:
            print(f"AI Review ({timeframe}) Generated.")

        # 2. Obsidian保存
        saved_path = ""
        if output_obsidian:
            writer = ObsidianWriter()
            report_content = ai_response.obsidian_report
            if graph_path:
                report_content += f"\n\n## 📊 Asset Trend\n![[{os.path.basename(graph_path)}]]\n"
            saved_path = writer.write_report(report_content)

        # 3. Slack通知
        if output_slack:
            notifier = SlackNotifier()
            model_info = f" (Model: {ai_response.model_name})" if ai_response.model_name else ""
            notifier.send_block_kit(
                title=f"家計簿AIレビュー ({timeframe}){model_info}",
                report=ai_response.slack_report,
                actions=ai_response.actions,
                score=ai_response.totonoi_score
            )
            if graph_path:
                notifier.upload_file(graph_path, f"資産推移グラフ ({timeframe})")

        # 4. 分析履歴を保存
        db.save_analysis(
            timeframe=timeframe, 
            summary=ai_response.slack_report, 
            report_path=saved_path or "", 
            score=ai_response.totonoi_score, 
            raw_response=json.dumps(ai_response.model_dump(), ensure_ascii=False),
            model_name=ai_response.model_name,
            prompt_tokens=ai_response.prompt_tokens,
            response_tokens=ai_response.response_tokens,
            total_tokens=ai_response.total_tokens
        )
        return ai_response

    except Exception as e:
        print(f"Error in run_review: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    setup_windows_encoding()
    parser = argparse.ArgumentParser(description="Kakeibo AI Review System")
    parser.add_argument("--source", type=str, choices=["mf", "zaim"], default="mf", help="データソース (mf or zaim)")
    parser.add_argument("--timeframe", type=str, choices=["daily", "weekly", "monthly", "quarterly", "yearly"], help="分析のタイムフレーム")
    parser.add_argument("--headless", action="store_true", default=True, help="ブラウザを非表示で実行")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="ブラウザを表示して実行")
    parser.add_argument("--fetch-only", action="store_true", help="データ取得のみ実行")
    parser.add_argument("--skip-fetch", action="store_true", help="データ取得をスキップして既存DBから分析")
    parser.add_argument("--db-path", type=str, default="local/kakeibo.db", help="SQLite DBのパス")
    
    # 出力制御フラグ
    parser.add_argument("--console", action="store_true", default=True, help="コンソールに結果を表示")
    parser.add_argument("--no-console", action="store_false", dest="console", help="コンソール表示を無効化")
    parser.add_argument("--slack", action="store_true", default=True, help="Slack通知を有効化")
    parser.add_argument("--no-slack", action="store_false", dest="slack", help="Slack通知を無効化")
    parser.add_argument("--obsidian", action="store_true", default=True, help="Obsidian保存を有効化")
    parser.add_argument("--no-obsidian", action="store_false", dest="obsidian", help="Obsidian保存を無効化")
    
    args = parser.parse_args()

    # 実行対象のタイムフレームを決定
    target_timeframes = []
    if args.timeframe:
        target_timeframes = [args.timeframe]
    else:
        schedule = load_config("local/config/schedule.json")
        target_timeframes = get_scheduled_timeframes(schedule)
        if not target_timeframes:
            print("No task scheduled. Defaulting to weekly for manual run.")
            target_timeframes = ["weekly"]

    # fetch-onlyの場合はデータ取得のみ
    if args.fetch_only:
        run_review(
            timeframe=target_timeframes[0],
            source=args.source,
            headless=args.headless,
            skip_fetch=False,
            db_path=args.db_path,
            output_slack=False,
            output_obsidian=False,
            output_console=False
        )
        return

    # 各タイムフレームを実行
    current_skip_fetch = args.skip_fetch
    for i, tf in enumerate(target_timeframes):
        print(f"\n🚀 Starting Review for timeframe: {tf}")
        run_review(
            timeframe=tf,
            source=args.source,
            headless=args.headless,
            skip_fetch=current_skip_fetch,
            db_path=args.db_path,
            output_slack=args.slack,
            output_obsidian=args.obsidian,
            output_console=args.console
        )
        # 2回目以降は、fetchをスキップするように設定（初回で取得済みの前提）
        if not args.skip_fetch:
            current_skip_fetch = True

if __name__ == "__main__":
    main()
