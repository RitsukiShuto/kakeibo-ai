import os
import threading
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
def handle_review_command(ack, command, say, client):
    """
    Slackからのオンデマンド分析実行コマンド (/review)
    """
    ack()
    user_id = command["user_id"]
    timeframe = command.get("text", "weekly").strip()
    if timeframe not in ["weekly", "monthly", "quarterly", "yearly"]:
        timeframe = "weekly"

    say(f"🆗 了解！{timeframe}の家計簿を分析してくるから、ちょっと待っててね！✨")
    
    # 分析は時間がかかるため、別スレッドで実行
    def run_async_analysis():
        try:
            # 最新データを取得して分析 (headless=True)
            result = run_review(timeframe=timeframe, headless=True)
            if not result:
                client.chat_postEphemeral(
                    channel=command["channel_id"],
                    user=user_id,
                    text="❌ ごめん、分析中にエラーが出ちゃったみたい...。後でもう一回試してみて！"
                )
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
