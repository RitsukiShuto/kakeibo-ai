import os
import json
import sys
from datetime import datetime
from src.analyzer.gemini_analyzer import GeminiAnalyzer
from src.output.slack_notifier import SlackNotifier
from src.output.obsidian_writer import ObsidianWriter
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

INPUT_FILE = "input_data.json"

def main():
    # 0. タイムフレームの取得（引数がない場合は monthly）
    timeframe = "monthly"
    if len(sys.argv) > 1:
        valid_timeframes = ["daily", "weekly", "monthly", "yearly"]
        arg = sys.argv[1].lower()
        if arg in valid_timeframes:
            timeframe = arg
        else:
            print(f"警告: 無効なタイムフレーム '{arg}' が指定されました。デフォルトの 'monthly' で実行します。")

    print(f"=== AI 分析フェーズ ({timeframe.upper()}) ===")
    
    # 1. インプットデータの読み込み
    if not os.path.exists(INPUT_FILE):
        print(f"エラー: インプットファイル '{INPUT_FILE}' が見つかりません。")
        print("先に 'python prepare_input.py' を実行してデータを用意してください。")
        return

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            input_data = json.load(f)
        
        transactions = input_data.get("transactions", [])
        generated_at = input_data.get("generated_at", "Unknown")
        
        if not transactions:
            print("分析対象の明細データが空です。")
            return

        print(f"データ読み込み完了: {len(transactions)} 件 (データ取得日時: {generated_at})")

        # 2. AI 分析 (Gemini)
        analyzer = GeminiAnalyzer()
        report_content = analyzer.analyze_kakeibo(transactions, timeframe=timeframe)
        
        if not report_content:
            print("AI からのレスポンスが空です。分析に失敗しました。")
            return

        # 3. Obsidian 保存
        writer = ObsidianWriter()
        # メタデータを先頭に追加
        header = f"> [!meta] Analysis Type: {timeframe.upper()}\n"
        header += f"> [!meta] Data Date: {generated_at}\n\n"
        final_content = header + report_content
        
        saved_path = writer.write_report(final_content)
        
        if saved_path:
            print(f"詳細レポートを保存しました: {saved_path}")

        # 4. Slack 通知
        notifier = SlackNotifier()
        # レポートの冒頭部分を抽出して通知
        summary_text = report_content[:500] + "..." if len(report_content) > 500 else report_content
        
        today = datetime.now().strftime("%Y-%m-%d")
        slack_title = f"{today} 家計簿 AI レビュー ({timeframe.upper()})"
        slack_body = f"マネーフォワードから取得したデータを分析しました。\n\n{summary_text}"
        
        notifier.send_notification(slack_title, slack_body)
        
        print(f"\n=== {timeframe.upper()} 分析工程が完了しました ===")

    except Exception as e:
        print(f"分析実行中にエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
