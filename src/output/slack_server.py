import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

# App Token (xapp-...) と Bot Token (xoxb-...) が必要です
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

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
