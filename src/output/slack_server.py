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

load_dotenv()

# App Token (xapp-...) と Bot Token (xoxb-...) が必要です
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.command("/review")
def handle_review_command(ack, command, respond, client):
    """
    Slackからのオンデマンド分析実行コマンド (/review)
    """
    ack()
    user_id = command["user_id"]
    raw_text = command.get("text", "").strip().lower()
    
    skip_fetch = "skip" in raw_text
    timeframe_str = raw_text.replace("skip", "").strip()

    if timeframe_str in ["m", "monthly"]:
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

    thread = threading.Thread(target=run_async_analysis)
    thread.start()

@app.action("action_done")
def handle_action_done(ack, body, logger):
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

def start_slack_server():
    if not SLACK_APP_TOKEN:
        print("Error: SLACK_APP_TOKEN is not set. Slack server cannot start.")
        return
    
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    print("⚡️ Slack Socket Mode Server is running...")
    handler.start()

if __name__ == "__main__":
    start_slack_server()
