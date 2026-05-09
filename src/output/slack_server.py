import os
import sys
import threading
from datetime import datetime

# プロジェクトルートディレクトリをインポートパスに追加
# slack_server.py は src/output/ にあるため、3階層上がルート
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from main import run_review
from src.db.database import Database
import time

load_dotenv(os.path.join(ROOT_DIR, "local/.env"))

# App Token (xapp-...) と Bot Token (xoxb-...) が必要です
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
DB_PATH = os.getenv("KAKEIBO_DB_PATH", os.path.join(ROOT_DIR, "local/kakeibo.db"))

def start_heartbeat():
    """
    生存確認用スレッド (UTC)
    """
    try:
        db = Database(db_path=DB_PATH)
        print(f"💓 Heartbeat thread started. Target DB: {DB_PATH}")
        while True:
            try:
                db.update_heartbeat("slack")
            except Exception as e:
                print(f"Error updating heartbeat: {e}")
            time.sleep(60)
    except Exception as e:
        print(f"Failed to initialize heartbeat thread: {e}")

# テスト実行時やインポート時のエラーを防ぐため、未設定時はダミーを入れる
# token_verification_enabled=False を指定して、初期化時の Slack API 通信（auth.test）を無効化する
app = App(token=SLACK_BOT_TOKEN or "xoxb-dummy", token_verification_enabled=False)

@app.command("/review")
def handle_review_command(ack, command, respond, client):
    """
    Slackからのオンデマンド分析実行コマンド (/review)
    """
    try:
        ack()
        user_id = command["user_id"]
        raw_text = command.get("text", "").strip().lower()
        
        skip_fetch = "skip" in raw_text
        timeframe_str = raw_text.replace("skip", "").strip()

        if timeframe_str in ["d", "daily"]:
            timeframe = "daily"
        elif timeframe_str in ["m", "monthly"]:
            timeframe = "monthly"
        elif timeframe_str in ["y", "yearly"]:
            timeframe = "yearly"
        elif timeframe_str in ["q", "quarterly"]:
            timeframe = "quarterly"
        else:
            timeframe = "weekly"

        skip_msg = " (データ取得はスキップして爆速でいくよ！🚀)" if skip_fetch else ""
        respond(f"🆗 了解！{timeframe}の家計簿を分析してくるから、ちょっと待っててね！✨{skip_msg}")
        
        # 分析は時間がかかるため、別スレッドで実行
        def run_async_analysis():
            try:
                # 最新データを取得して分析 (headless=True)
                result = run_review(timeframe=timeframe, headless=True, skip_fetch=skip_fetch)
                if not result:
                    respond("❌ ごめん、分析中にエラーが出ちゃったみたい...。後でもう一回試してみて！")
            except Exception as e:
                print(f"Error in async analysis: {e}")
                respond(f"❌ 分析中に致命的なエラーが発生しました: {str(e)}")

        thread = threading.Thread(target=run_async_analysis)
        thread.start()
    except Exception as e:
        print(f"Error handling /review command: {e}")

@app.action("action_done")
def handle_action_done(ack, body, logger):
    try:
        ack()
        user_id = body["user"]["id"]
        action_id = body["actions"][0]["value"]
        
        # 本来はここでDBに「アクション完了」を記録する
        print(f"User {user_id} completed action: {action_id}")
        
        # 応答メッセージ
        app.client.chat_postMessage(
            channel=user_id,
            text=f"✨ マジ！？「{action_id}」達成したとか、せんぱい天才すぎ！アガる〜！💖"
        )
    except Exception as e:
        print(f"Error handling action_done: {e}")

def start_slack_server():
    print("🚀 Starting Slack Socket Mode Server...")
    if not SLACK_APP_TOKEN or not SLACK_BOT_TOKEN or SLACK_BOT_TOKEN == "xoxb-dummy":
        print("❌ Error: SLACK_APP_TOKEN or SLACK_BOT_TOKEN is not set correctly.")
        print(f"BOT_TOKEN ends with: {SLACK_BOT_TOKEN[-4:] if SLACK_BOT_TOKEN else 'None'}")
        return
    
    # 生存確認スレッドの開始
    heartbeat_thread = threading.Thread(target=start_heartbeat, daemon=True)
    heartbeat_thread.start()
    
    try:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        print("⚡️ Slack Socket Mode Server is running and connected!")
        handler.start()
    except Exception as e:
        print(f"❌ Critical Error in Slack Server: {e}")

if __name__ == "__main__":
    start_slack_server()
