import sys
import os

# プロジェクトのルートをパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.output.slack_notifier import SlackNotifier
from src.models import AIAction

def test_slack():
    print("=== Slack Notification Test Start ===")
    
    notifier = SlackNotifier()
    
    title = "テスト分析レポート (Debug)"
    summary = "これはテスト通知です。マネーフォワードからの資産取得とAI分析の連携テストを想定しています。ギャル風のメッセージが届くかチェックしてね！✨"
    
    actions = [
        AIAction(command="Now", description="テストボタン1をクリックして動作を確認せよ！"),
        AIAction(command="Keep", description="現状の爆アゲ設定を維持して資産を増やそう！")
    ]
    
    score = 85

    try:
        notifier.send_block_kit(
            title=title,
            summary=summary,
            actions=actions,
            score=score
        )
        print("Successfully sent message to Slack!")
    except Exception as e:
        print(f"Failed to send to Slack: {e}")

if __name__ == "__main__":
    test_slack()
