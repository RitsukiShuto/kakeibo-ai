#!/bin/bash

# 環境変数をcronに引き継ぐための処理
# .env や docker-compose の env_file から渡された変数をファイルに書き出す
printenv | grep -v "no_proxy" >> /etc/environment

# crontabファイルを登録
crontab /app/infra/docker/crontab

echo "Starting cron daemon..."
# cronをフォアグラウンドで起動
cron -f
