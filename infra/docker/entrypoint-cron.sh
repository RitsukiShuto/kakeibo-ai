#!/bin/bash

# 環境変数をcronに引き継ぐための処理
# .env や docker-compose の env_file から渡された変数をファイルに書き出す
printenv | grep -v "no_proxy" >> /etc/environment
cat << 'EOF' > /app/infra/docker/run_cron.sh
#!/bin/bash
set -a
source /etc/environment
set +a
cd /app && /usr/bin/python main.py >> /app/logs/cron_execution.log 2>&1
EOF
chmod +x /app/infra/docker/run_cron.sh

# crontabファイルを登録
crontab /app/infra/docker/crontab

echo "Starting cron daemon..."
# cronをフォアグラウンドで起動
cron -f
