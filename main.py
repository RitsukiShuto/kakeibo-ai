import argparse
import sys
import json
import os
import io
from datetime import datetime

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
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_scheduled_timeframe(schedule):
    """
    スケジュール設定に基づき、今日実行すべきタイムフレームを返す
    """
    today = datetime.now()
    weekday = today.strftime("%A") # Monday, Tuesday, ...
    day = today.day
    month = today.month

    reports = schedule.get("reports", {})
    
    if reports.get("yearly", {}).get("enabled") and month == reports["yearly"].get("month") and day == 1:
        return "yearly"
    
    if reports.get("quarterly", {}).get("enabled") and month in reports["quarterly"].get("months", []) and day == 1:
        return "quarterly"
    
    if reports.get("monthly", {}).get("enabled") and day == reports["monthly"].get("target_day", 1):
        return "monthly"
    
    if reports.get("weekly", {}).get("enabled") and weekday == reports["weekly"].get("target_day", "Monday"):
        return "weekly"
    
    return None

def run_review(timeframe: str = None, source: str = "mf", headless: bool = True, skip_fetch: bool = False, db_path: str = "local/kakeibo.db", output_slack: bool = True, output_obsidian: bool = True, output_console: bool = True, progress_callback=None):
    """
    家計簿レビューのメイン工程を実行する (CLIとSlackサーバーの両方から呼び出し可能)
    """
    schedule = load_config("local/config/schedule.json")
    profile = load_config("local/config/profile.json")
    budget = load_config("local/config/budget.json")

    if not timeframe:
        timeframe = get_scheduled_timeframe(schedule)
        if not timeframe:
            print("No task scheduled. Defaulting to weekly for manual run.")
            timeframe = "weekly"

    db = Database(db_path=db_path)
    fetcher = MoneyForwardFetcher() if source == "mf" else ZaimFetcher()

    try:
        if not skip_fetch:
            if progress_callback: progress_callback("🔄 マネーフォワードから入出金履歴を取得中...（少し時間がかかります）")
            print(f"Fetching transactions from {source}...")
            transactions = fetcher.fetch_transactions(headless=headless)
            if transactions:
                db.save_transactions(transactions)
            
            if progress_callback: progress_callback("🔄 続いて資産データを取得中...")
            print(f"Fetching assets from {source}...")
            assets = fetcher.fetch_assets(headless=headless)
            if assets:
                db.save_assets(assets)
        
        if progress_callback: progress_callback(f"🧠 データ取得完了！{timeframe}の家計簿をAIが分析中...（ギャルが本気出してます💅✨）")
        print(f"Starting AI Analysis ({timeframe})...")
        analyzer = GeminiAnalyzer()
        
        new_transactions = db.get_new_transactions_since_last_analysis(timeframe)
        asset_summary = db.get_asset_category_summary()
        latest_analysis = db.get_latest_analysis(timeframe)
        previous_summary = latest_analysis["summary"] if latest_analysis else None
        
        ai_response = analyzer.analyze_kakeibo(
            data=new_transactions, 
            assets_summary=asset_summary,
            timeframe=timeframe,
            profile=profile,
            budget=budget,
            previous_summary=previous_summary
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
            print(f"AI Review ({timeframe}) Generated: {ai_response.slack_report}")

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
            notifier.send_block_kit(
                title=f"家計簿AIレビュー ({timeframe})",
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
            raw_response=json.dumps(ai_response.model_dump(), ensure_ascii=False)
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
    parser.add_argument("--timeframe", type=str, choices=["weekly", "monthly", "quarterly", "yearly"], help="分析のタイムフレーム")
    parser.add_argument("--headless", action="store_true", default=True, help="ブラウザを非表示で実行 (MF用)")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="ブラウザを表示して実行 (MF用)")
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

    print(f"--- Kakeibo AI Review Task Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    print(f"Source: {args.source}, Headless: {args.headless}")

    schedule = load_config("local/config/schedule.json")
    profile = load_config("local/config/profile.json")
    budget = load_config("local/config/budget.json")

    timeframe = args.timeframe
    fetch_only = args.fetch_only
    if not timeframe and not fetch_only:
        timeframe = get_scheduled_timeframe(schedule)
        if timeframe:
            print(f"Scheduled Task Detected: {timeframe}")
        else:
            print("No task scheduled for today. Fetching data only.")
            fetch_only = True

    db = Database(db_path=args.db_path)
    fetcher = MoneyForwardFetcher() if args.source == "mf" else ZaimFetcher()

    try:
        if not args.skip_fetch:
            print(f"Fetching transactions from {args.source}...")
            transactions = fetcher.fetch_transactions(headless=args.headless)
            if transactions:
                db.save_transactions(transactions)
                print(f"Saved {len(transactions)} transactions to DB.")
            
            print(f"Fetching assets from {args.source}...")
            assets = fetcher.fetch_assets(headless=args.headless)
            if assets:
                db.save_assets(assets)
                print(f"Saved {len(assets)} asset records to DB.")
        else:
            print("Skip-fetch enabled. Using existing data in DB.")

        if fetch_only:
            print("Fetch only mode. Skipping analysis.")
            return

        print(f"Starting AI Analysis ({timeframe})...")
        analyzer = GeminiAnalyzer()
        
        new_transactions = db.get_new_transactions_since_last_analysis(timeframe)
        # 集計済みサマリーを使用
        asset_summary = db.get_asset_category_summary()
        
        latest_analysis = db.get_latest_analysis(timeframe)
        previous_summary = latest_analysis["summary"] if latest_analysis else None
        
        ai_response = analyzer.analyze_kakeibo(
            data=new_transactions, 
            assets_summary=asset_summary,
            timeframe=timeframe,
            profile=profile,
            budget=budget,
            previous_summary=previous_summary
        )

        if not ai_response:
            print("Analysis failed.")
            return

        # --- 出力セクション ---
        saved_path = ""
        graph_path = ""
        
        # 0. グラフの生成
        try:
            visualizer = Visualizer()
            graph_path = visualizer.generate_asset_trend_graph(db_path=args.db_path)
            if graph_path:
                print(f"資産推移グラフを生成しました: {graph_path}")
        except Exception as e:
            print(f"グラフ生成に失敗しました: {e}")

        # 1. コンソール出力
        if args.console:
            output_text = "\n" + "="*50 + "\n"
            output_text += f"🤖 AI分析レポート ({timeframe})\n"
            output_text += "-" * 50 + "\n"
            output_text += f"【詳細】\n{ai_response.slack_report}\n\n"
            
            output_text += f"【予算状況 (予実)】:\n"
            for b in ai_response.budget_status:
                output_text += f" - {b.category}: {b.actual:,} / {b.budget:,}円 ({b.status})\n"
            output_text += "\n"

            output_text += f"【資産内訳】:\n"
            total_calc = 0
            for asset in ai_response.asset_breakdown:
                output_text += f" - {asset.category}: {asset.amount:,}円\n"
                total_calc += asset.amount
            output_text += f" **合計: {total_calc:,}円**\n\n"

            output_text += f"【ととのい指数】: {ai_response.totonoi_score}\n"
            output_text += f"【アクション】:\n"
            for action in ai_response.actions:
                output_text += f" - [{action.command}] {action.description}\n"
            output_text += "="*50 + "\n"
            
            print(output_text)
            
            # コンソールの文字化け対策兼、控えとしてファイルにも保存
            try:
                with open("latest_review.md", "w", encoding="utf-8") as f:
                    f.write(output_text)
                    f.write("\n\n--- Detailed Report (Obsidian Format) ---\n")
                    f.write(ai_response.obsidian_report)
                print(f"分析結果の控えを latest_review.md に保存しました。")
            except Exception as e:
                print(f"ファイル保存に失敗しました: {e}")

        # 2. Obsidian保存
        if args.obsidian:
            writer = ObsidianWriter()
            report_content = ai_response.obsidian_report
            if graph_path:
                # Obsidian用に画像リンクを追記（ローカルパスなので環境に依存しますが）
                report_content += f"\n\n## 📊 Asset Trend\n![[{os.path.basename(graph_path)}]]\n"
            saved_path = writer.write_report(report_content)

        # 3. Slack通知
        if args.slack:
            notifier = SlackNotifier()
            try:
                notifier.send_block_kit(
                    title=f"家計簿AIレビュー ({timeframe})",
                    report=ai_response.slack_report,
                    actions=ai_response.actions,
                    score=ai_response.totonoi_score
                )
                if graph_path:
                    notifier.upload_file(graph_path, f"資産推移グラフ ({timeframe})")
            except Exception as e:
                print(f"Slack notification failed: {e}")

        # 4. 分析履歴を保存
        db.save_analysis(
            timeframe=timeframe, 
            summary=ai_response.slack_report, 
            report_path=saved_path or "", 
            score=ai_response.totonoi_score, 
            raw_response=json.dumps(ai_response.model_dump(), ensure_ascii=False)
        )

        print(f"--- Kakeibo AI Review Successfully Completed ---")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
