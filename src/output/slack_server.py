import os
import sys
import threading
from datetime import datetime

# プロジェクトルートディレクトリをインポートパスに追加
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from main import run_review, load_config
from src.db.database import Database
import time

load_dotenv(os.path.join(ROOT_DIR, "local/.env"))

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
DB_PATH = os.getenv("KAKEIBO_DB_PATH", os.path.join(ROOT_DIR, "local/kakeibo.db"))

def start_heartbeat():
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

app = App(token=SLACK_BOT_TOKEN or "xoxb-dummy", token_verification_enabled=False)

# ------------------------------------------------------------------------------
# 共通コマンド: /kakeibo [action] [args]
# ------------------------------------------------------------------------------
@app.command("/kakeibo")
def handle_kakeibo_command(ack, command, respond):
    ack()
    raw_text = command.get("text", "").strip()
    parts = raw_text.split()
    
    action = parts[0].lower() if parts else "help"
    args = parts[1:] if len(parts) > 1 else []

    if action == "check":
        handle_check(respond, args)
    elif action == "stats":
        handle_stats(respond, args)
    elif action == "character":
        handle_character(respond, args)
    elif action == "last":
        handle_last(respond)
    elif action == "review":
        # /kakeibo review [timeframe] [skip]
        handle_review_logic(respond, args)
    else:
        handle_help(respond)

# ------------------------------------------------------------------------------
# 既存の /review も維持しつつ、共通ロジックへ誘導
# ------------------------------------------------------------------------------
@app.command("/review")
def handle_review_command(ack, command, respond):
    ack()
    raw_text = command.get("text", "").strip()
    args = raw_text.split()
    handle_review_logic(respond, args)

def handle_review_logic(respond, args):
    """分析実行ロジック"""
    skip_fetch = "skip" in [a.lower() for a in args]
    timeframe_args = [a.lower() for a in args if a.lower() != "skip"]
    
    tf_map = {"d": "daily", "m": "monthly", "w": "weekly", "y": "yearly", "q": "quarterly"}
    timeframe = tf_map.get(timeframe_args[0], timeframe_args[0]) if timeframe_args else "weekly"
    
    if timeframe not in ["daily", "weekly", "monthly", "quarterly", "yearly"]:
        timeframe = "weekly"

    skip_msg = " (データ取得はスキップして爆速でいくよ！🚀)" if skip_fetch else ""
    respond(f"🆗 了解！{timeframe}の家計簿を分析してくるから、ちょっと待っててね！✨{skip_msg}")
    
    def run_async_analysis():
        try:
            result = run_review(timeframe=timeframe, headless=True, skip_fetch=skip_fetch)
            if not result:
                respond("❌ ごめん、分析中にエラーが出ちゃったみたい...。後でもう一回試してみて！")
        except Exception as e:
            respond(f"❌ 分析中に致命的なエラーが発生しました: {str(e)}")

    threading.Thread(target=run_async_analysis).start()

def handle_check(respond, args):
    """予算チェックロジック"""
    try:
        db = Database(db_path=DB_PATH)
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        
        # 予算データの読み込み
        config_dir = os.path.join(ROOT_DIR, "local/config")
        from main import load_config
        budget_data = load_config(os.path.join(config_dir, "budget.json"))
        
        # 実績の取得 (簡易計算)
        import sqlite3
        import pandas as pd
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment'"
        actual = pd.read_sql_query(query, conn)['total'].iloc[0] or 0
        conn.close()
        
        # カテゴリ別予算の集計
        monthly = budget_data.get("monthly", {})
        total_budget = sum(monthly.get("categories", {}).values())
        
        remaining = total_budget - actual
        percent = (actual / total_budget * 100) if total_budget > 0 else 0
        
        status_msg = "いい感じ！" if percent < 80 else "ちょっと使いすぎかも？注意してね！"
        
        respond(
            f"📊 *今月の予算状況 ({current_month})*\n"
            f"• 予算合計: {total_budget:,}円\n"
            f"• 現在の実績: {actual:,}円 ({percent:.1f}%)\n"
            f"• *残り: {remaining:,}円*\n\n"
            f"👉 {status_msg}✨"
        )
    except Exception as e:
        respond(f"❌ 状況の取得に失敗しました: {e}")

def handle_stats(respond, args):
    """統計・使用量ロジック"""
    if "ai" in [a.lower() for a in args]:
        try:
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT SUM(prompt_tokens), SUM(response_tokens), SUM(total_tokens) FROM analysis_history WHERE created_at >= date('now', 'start of month')")
            row = cur.fetchone()
            conn.close()
            
            p, r, t = row if row and row[0] else (0, 0, 0)
            respond(
                f"🤖 *今月の AI 使用量統計*\n"
                f"• プロンプト: {p or 0:,} tokens\n"
                f"• レスポンス: {r or 0:,} tokens\n"
                f"• *合計: {t or 0:,} tokens*\n\n"
                f"無料枠を賢く使って節約中だよ！💅✨"
            )
        except Exception as e:
            respond(f"❌ 統計の取得に失敗しました: {e}")
    else:
        respond("💡 `stats ai` と打つと、AIのトークン使用量が見れるよ！")

def handle_character(respond, args):
    """キャラクター切り替え（モック）"""
    if not args:
        respond("👗 *現在のキャラ設定*: ギャル (デフォルト)\n切り替えたい時は `character cool` や `character gentle` って打ってね！（※開発中だよ！）")
    else:
        respond(f"✨ キャラクターを `{args[0]}` に設定したよ！(※現在は表示上の変更のみです。次回の分析から反映されるように頑張るね！)")

def handle_last(respond):
    """最新レポート表示"""
    try:
        db = Database(db_path=DB_PATH)
        latest = db.get_latest_analysis("daily") or db.get_latest_analysis("monthly")
        if latest:
            respond(f"📝 *最新の分析結果 ({latest['timeframe']})*\n---\n{latest['summary']}")
        else:
            respond("まだ分析データがないみたいだよ！")
    except Exception as e:
        respond(f"❌ エラーが発生しました: {e}")

def handle_help(respond):
    respond(
        "👋 *Kakeibo AI スラッシュコマンド・ヘルプ*\n\n"
        "• `/kakeibo check` : 今月の残予算を確認するよ！💰\n"
        "• `/kakeibo last`  : 最新の分析レポートを再表示するよ！📝\n"
        "• `/kakeibo stats ai` : AIのトークン使用量を確認できるよ！🤖\n"
        "• `/kakeibo review [tf]` : 指定した期間で分析を開始するよ！(tf: daily, weekly, etc)\n"
        "• `/kakeibo help`  : このヘルプを表示するよ！\n\n"
        "既存の `/review [tf]` も今まで通り使えるから安心してね！✨"
    )

@app.action("action_done")
def handle_action_done(ack, body, logger):
    try:
        ack()
        user_id = body["user"]["id"]
        action_id = body["actions"][0]["value"]
        print(f"User {user_id} completed action: {action_id}")
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
        return
    
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
