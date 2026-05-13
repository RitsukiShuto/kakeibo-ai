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

# ベースディレクトリの設定
LOCAL_DIR = os.getenv("KAKEIBO_LOCAL_DIR", "local")
load_dotenv(os.path.join(ROOT_DIR, LOCAL_DIR, ".env"))

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
DB_PATH = os.getenv("KAKEIBO_DB_PATH", os.path.join(ROOT_DIR, LOCAL_DIR, "kakeibo.db"))

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
# スラッシュコマンドの実装
# ------------------------------------------------------------------------------

@app.command("/kakeibo-review")
def handle_review_command(ack, command, respond):
    """家計簿の分析を実行します。[分析モード] [データ取得]"""
    ack()
    raw_text = command.get("text", "").strip()
    args = raw_text.split()
    handle_review_logic(respond, args)

@app.command("/kakeibo-help")
def handle_help_command(ack, command, respond):
    """ヘルプを参照します"""
    ack()
    handle_help(respond)

@app.command("/kakeibo-model")
def handle_model_command(ack, command, respond):
    """分析に使用するモデルを変更します"""
    ack()
    raw_text = command.get("text", "").strip()
    args = raw_text.split()
    handle_model_logic(respond, args)

@app.command("/kakeibo-check")
def handle_check_command(ack, command, respond):
    """今月の残予算と進捗率を即座に表示します"""
    ack()
    handle_check(respond)

@app.command("/kakeibo-stats-ai")
def handle_stats_ai_command(ack, command, respond):
    """今月の合計トークン使用量を表示します"""
    ack()
    handle_stats_ai(respond)

@app.command("/kakeibo-last")
def handle_last_command(ack, command, respond):
    """最新の分析レポートを再表示します"""
    ack()
    handle_last(respond)

# ------------------------------------------------------------------------------
# イベントハンドラ
# ------------------------------------------------------------------------------

@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    """メンション時にチャット回答する"""
    event = body["event"]
    user_id = event["user"]
    text = event["text"]
    
    # メンション部分を削除
    # 例: <@U12345678> こんにちは -> こんにちは
    clean_text = re.sub(r"<@.*?>", "", text).strip()
    
    if not clean_text:
        say(f"はい、<@{user_id}>さん！何かお手伝いできることはありますか？✨\n`/kakeibo-help` でコマンド一覧が見れるよ！")
        return

    handle_chat_logic(say, user_id, clean_text)

@app.event("message")
def handle_message_events(body, say, logger):
    """DM時にチャット回答する"""
    event = body["event"]
    # チャンネルタイプが 'im' (DM) の場合のみ反応
    if event.get("channel_type") != "im":
        return
    # ボット自身のメッセージには反応しない
    if event.get("bot_id"):
        return
        
    user_id = event["user"]
    text = event["text"]
    handle_chat_logic(say, user_id, text)

# ------------------------------------------------------------------------------
# ロジックの実装
# ------------------------------------------------------------------------------

import re
import json

def handle_chat_logic(say, user_id, message):
    """チャット回答の共通ロジック"""
    # 読み込み中を伝える
    # say("🤔 考えてるからちょっと待ってね...")
    
    def run_async_chat():
        try:
            db = Database(db_path=DB_PATH)
            config_dir = os.path.join(ROOT_DIR, "local/config")
            
            # コンテキスト情報の取得
            import sqlite3
            import pandas as pd
            from src.models import Transaction
            from datetime import date
            
            conn = sqlite3.connect(DB_PATH)
            query_tx = "SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 10"
            df_tx = pd.read_sql_query(query_tx, conn)
            recent_transactions = [Transaction(
                transaction_id=row['transaction_id'],
                transaction_date=date.fromisoformat(row['transaction_date']),
                category=row['category'],
                genre=row['genre'],
                amount=row['amount'],
                comment=row['comment'],
                source=row['source'],
                mode=row['mode']
            ) for _, row in df_tx.iterrows()]
            conn.close()
            
            asset_summary = db.get_asset_category_summary()
            profile = load_config(os.path.join(config_dir, "profile.json"))
            budget = load_config(os.path.join(config_dir, "budget.json"))
            
            from src.analyzer.gemini_analyzer import GeminiAnalyzer
            analyzer = GeminiAnalyzer()
            
            # Slackのメンションには履歴は一旦含めない（簡易化のため）
            response = analyzer.chat(
                message=message,
                history=None,
                profile=profile,
                budget=budget,
                assets_summary=asset_summary,
                recent_transactions=recent_transactions
            )
            
            say(f"<@{user_id}> {response}")
            
        except Exception as e:
            print(f"Chat logic error: {e}")
            say(f"❌ ごめん、エラーになっちゃった...: `{e}`")

    threading.Thread(target=run_async_chat).start()

def handle_review_logic(respond, args):
    """分析実行ロジック"""
    skip_fetch = "skip" in [a.lower() for a in args]
    timeframe_args = [a.lower() for a in args if a.lower() != "skip"]
    
    tf_map = {"d": "daily", "m": "monthly", "w": "weekly", "y": "yearly", "q": "quarterly"}
    timeframe = tf_map.get(timeframe_args[0], timeframe_args[0]) if timeframe_args else "weekly"
    
    if timeframe not in ["daily", "weekly", "monthly", "quarterly", "yearly"]:
        timeframe = "weekly"

    initial_msg = f"🆗 了解！{timeframe}の家計簿を分析するよ！✨"
    if not skip_fetch:
        initial_msg += "\n🔄 まずは最新のデータを取得してくるね。1分くらいかかるかも！"
    else:
        initial_msg += " (データ取得はスキップして爆速でいくよ！🚀)"
    
    respond(initial_msg)
    
    def run_async_analysis():
        def progress_update(msg):
            try:
                respond(msg)
            except: pass

        try:
            # 最新データを取得して分析
            # run_review 内でエラーが発生した場合は例外が飛ぶ想定
            result = run_review(
                timeframe=timeframe, 
                headless=True, 
                skip_fetch=skip_fetch,
                progress_callback=progress_update
            )
            if not result:
                respond("❌ ごめん、分析結果が空だったみたい...。設定やデータを確認してみて！")
        except Exception as e:
            error_msg = str(e)
            print(f"Error in async analysis: {e}")
            if "Timeout" in error_msg or "locator" in error_msg:
                respond("❌ MoneyForward へのログインでタイムアウトが発生したよ...。サーバーの負荷が高いか、セッションが切れちゃったかも。後でもう一度試してね！")
            else:
                respond(f"❌ 分析中にエラーが発生したよ: `{error_msg}`")

    threading.Thread(target=run_async_analysis).start()

def handle_model_logic(respond, args):
    """モデル切り替えロジック"""
    config_dir = os.path.join(ROOT_DIR, "local/config")
    settings_path = os.path.join(config_dir, "settings.json")
    
    available_models = {
        "pro": "gemini-pro-latest",
        "flash": "gemini-flash-latest",
        "lite": "gemini-flash-lite-latest"
    }

    if not args:
        # 現在のモデルを確認
        current = "flash"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    current = settings.get("ai", {}).get("active_model", "gemini-flash-latest")
            except: pass
        
        model_list = "\n".join([f"• `{k}`: {v}" for k, v in available_models.items()])
        respond(
            f"🤖 *現在の使用モデル*: `{current}`\n\n"
            f"切り替えたい時は以下のように打ってね！\n{model_list}\n"
            f"例: `/kakeibo-model pro`"
        )
    else:
        new_key = args[0].lower()
        if new_key in available_models:
            new_model = available_models[new_key]
            try:
                settings = {}
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                
                if "ai" not in settings: settings["ai"] = {}
                settings["ai"]["active_model"] = new_model
                
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                respond(f"✅ 使用モデルを `{new_model}` に変更したよ！次回の分析から適用されるよ！✨")
            except Exception as e:
                respond(f"❌ 設定の保存に失敗しました: {e}")
        else:
            respond(f"❌ `{new_key}` は有効な選択肢じゃないみたい...。`pro`, `flash`, `lite` から選んでね！")

def handle_check(respond):
    """予算チェックロジック"""
    try:
        db = Database(db_path=DB_PATH)
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        
        config_dir = os.path.join(ROOT_DIR, "local/config")
        budget_data = load_config(os.path.join(config_dir, "budget.json"))
        
        import sqlite3
        import pandas as pd
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment'"
        actual = pd.read_sql_query(query, conn)['total'].iloc[0] or 0
        conn.close()
        
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

def handle_stats_ai(respond):
    """AI使用量統計ロジック"""
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT SUM(prompt_tokens), SUM(response_tokens), SUM(total_tokens) FROM analysis_history WHERE created_at >= date('now', 'start of month')")
        row = cur.fetchone()
        conn.close()
        
        p, r, t = row if row and row[0] is not None else (0, 0, 0)
        respond(
            f"🤖 *今月の AI 使用量統計*\n"
            f"• プロンプト: {p or 0:,} tokens\n"
            f"• レスポンス: {r or 0:,} tokens\n"
            f"• *合計: {t or 0:,} tokens*\n\n"
            f"無料枠を賢く使って節約中だよ！💅✨"
        )
    except Exception as e:
        respond(f"❌ 統計の取得に失敗しました: {e}")

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
        "• `/kakeibo-check` : 今月の残予算と進捗率を確認するよ！💰\n"
        "• `/kakeibo-review [tf]` : 家計簿の分析を実行するよ！(tf: daily, weekly, etc)\n"
        "• `/kakeibo-model [m]` : 使用する AI モデルを変更するよ！(m: pro, flash, lite)\n"
        "• `/kakeibo-stats-ai` : 今月の AI トークン使用量を表示するよ！🤖\n"
        "• `/kakeibo-last` : 最新の分析レポートを再表示するよ！📝\n"
        "• `/kakeibo-help` : このヘルプを表示するよ！\n\n"
        "既存の `/review [tf]` も引き続き利用可能です！✨"
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
