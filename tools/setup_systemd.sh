#!/bin/bash

# ==============================================================================
# Raspberry Pi Systemd 移行 & セットアップスクリプト
# ==============================================================================

PROJECT_ROOT="/home/r410/kakeibo-ai"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== Systemd への移行処理を開始します ==="

# 1. 既存の Cron 設定の削除
echo "[1/4] 既存の Crontab 設定を確認・削除しています..."
crontab -l | grep -v "kakeibo-ai" | crontab -
# nohup で動いている Slack サーバーも停止
pkill -f "slack_server.py" || true

# 2. Service ファイルのコピー
echo "[2/4] Systemd 設定ファイルを配置しています..."
sudo cp "$PROJECT_ROOT/infra/systemd/"* "$SYSTEMD_DIR/"

# 3. 権限設定
echo "[3/4] デーモンをリロードしています..."
sudo systemctl daemon-reload

# 4. サービスの有効化と起動
echo "[4/4] サービスを有効化しています..."

# Slackサーバー
sudo systemctl enable kakeibo-slack.service
sudo systemctl start kakeibo-slack.service

# APIサーバー (Reactダッシュボード用)
sudo systemctl enable kakeibo-api.service
sudo systemctl start kakeibo-api.service

# Streamlitダッシュボード
sudo systemctl enable kakeibo-dashboard.service
sudo systemctl start kakeibo-dashboard.service

# 定期実行（Timer）
sudo systemctl enable kakeibo-review.timer
sudo systemctl start kakeibo-review.timer

echo -e "\n=== 移行が完了しました！ ==="
echo "Slackサーバーの状態確認: sudo systemctl status kakeibo-slack"
echo "APIサーバーの状態確認: sudo systemctl status kakeibo-api"
echo "ダッシュボードの状態確認: sudo systemctl status kakeibo-dashboard"
echo "定期実行タイマーの状態確認: sudo systemctl list-timers --all | grep kakeibo"
echo "ログの確認: journalctl -u kakeibo-api -f"
