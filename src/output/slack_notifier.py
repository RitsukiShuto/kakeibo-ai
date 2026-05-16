import os
import json
import re
from typing import List
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.models import AIAction
from src import __version__

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

class SlackNotifier:
    def __init__(self):
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.user_id = os.getenv("SLACK_USER_ID")
        self.client = WebClient(token=self.bot_token) if self.bot_token else None
        
        self.dashboard_url = os.getenv("DASHBOARD_URL")
        if not self.dashboard_url:
            self.dashboard_url = f"http://{self._get_local_ip()}:5173"

        if not self.bot_token:
            print("Warning: SLACK_BOT_TOKEN is not set.")
        if not self.user_id:
            print("Warning: SLACK_USER_ID is not set.")

    def _get_local_ip(self):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    def _format_mrkdwn(self, text: str) -> str:
        """
        標準的な Markdown を Slack の mrkdwn 形式に変換する
        """
        if not text:
            return ""
        
        # 1. 見出し (### Header) を 太字 (*Header*) に変換
        text = re.sub(r'^### (.*)$', r'*\1*', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*)$', r'*\1*', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*)$', r'*\1*', text, flags=re.MULTILINE)
        
        # 2. 太字 (**bold**) を Slackの太字 (*bold*) に変換
        # ※ 既に *bold* の形式になっている場合に重複しないよう注意
        text = text.replace("**", "*")
        
        return text

    def send_notification(self, title: str, text: str, channel: str = None):
        """
        簡易的なテキスト通知
        """
        target_channel = channel or self.user_id
        if not self.client or not target_channel:
            return

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"ℹ️ {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": self._format_mrkdwn(text)
                }
            }
        ]

        try:
            self.client.chat_postMessage(
                channel=target_channel,
                text=title,
                blocks=blocks
            )
        except Exception as e:
            print(f"Failed to send simple notification: {e}")

    def send_block_kit(self, title: str, report: str, actions: List[AIAction], score: int, model_name: str = None, total_tokens: int = None, channel: str = None):
        """
        Slack Web API を使用して DM を送信する
        """
        target_channel = channel or self.user_id
        if not self.client or not target_channel:
            print("Slack notification skipped: Missing token or user ID.")
            return

        # スコアに応じた絵文字
        score_emoji = "🔥" if score >= 80 else "✅" if score >= 50 else "⚠️"
        
        formatted_report = self._format_mrkdwn(report)

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
                    "text": f"*ととのい指数: {score_emoji} {score}*\n\n{formatted_report}"
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
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "やったよ！✨",
                        "emoji": True
                    },
                    "value": f"{action.command}: {action.description[:50]}",
                    "action_id": "action_done"
                }
            })

        blocks.append({
            "type": "divider"
        })
        context_text = f"詳細レポートは Obsidian または <{self.dashboard_url}|🌐 Webダッシュボード> でチェックしてね！✨ (v{__version__})"
        if model_name or total_tokens:
            token_str = f" / {total_tokens:,} tokens" if total_tokens else ""
            model_str = model_name or "AI"
            context_text += f" | 🤖 {model_str}{token_str}"

        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": context_text
                }
            ]
        })

        try:
            # chat.postMessage を使用して DM を送信
            # channel 引数に User ID を指定することで DM になる
            response = self.client.chat_postMessage(
                channel=target_channel,
                text=f"【家計簿AI】{title}", # 通知用プレーンテキスト
                blocks=blocks
            )
            if not response["ok"]:
                print(f"Error sending DM to Slack: {response['error']}")
        except SlackApiError as e:
            print(f"Slack API Error: {e.response['error']}")
        except Exception as e:
            print(f"Failed to send Slack DM: {e}")

    def upload_file(self, file_path: str, title: str, channel: str = None):
        """
        ファイルを Slack にアップロードし、DM に送信する
        """
        target_channel = channel or self.user_id
        if not self.client or not target_channel:
            return

        if not os.path.exists(file_path):
            print(f"Error: File not found for upload: {file_path}")
            return

        try:
            response = self.client.files_upload_v2(
                channel=target_channel,
                file=file_path,
                title=title,
                initial_comment=f"📊 {title}"
            )
            if not response["ok"]:
                print(f"Error uploading file to Slack: {response['error']}")
        except SlackApiError as e:
            print(f"Slack API Error (Upload): {e.response['error']}")
        except Exception as e:
            print(f"Failed to upload file to Slack: {e}")
