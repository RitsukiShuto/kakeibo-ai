import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from src.models import AIAction

load_dotenv()

class SlackNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            print("Warning: SLACK_WEBHOOK_URL is not set.")

    def send_notification(self, title: str, text: str):
        """
        簡易的なテキスト通知（互換性のため残す）
        """
        self.send_block_kit(title, text, [], 0)

    def send_block_kit(self, title: str, summary: str, actions: List[AIAction], score: int):
        """
        Slack Block Kit を使用したリッチな通知
        """
        if not self.webhook_url:
            return

        # スコアに応じた絵文字
        score_emoji = "🔥" if score >= 80 else "✅" if score >= 50 else "⚠️"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*ととのい指数: {score_emoji} {score}*\n{summary}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🚀 ギャル・コマンド (改善アクション)*"
                }
            }
        ]

        # アクションの追加
        for action in actions:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*[{action.command}]* {action.description}"
                }
            })

        blocks.append({
            "type": "divider"
        })
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "詳細レポートは Obsidian でチェックしてね！✨"
                }
            ]
        })

        payload = {"blocks": blocks}

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                print(f"Error sending to Slack: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
