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

# settings.json から定期実行設定を読み込み crontab を動的生成
python3 -c "
import json, os

settings_path = os.path.join(os.getenv('KAKEIBO_LOCAL_DIR', 'local'), 'config', 'settings.json')
log_path = '/app/logs/cron_execution.log'
os.makedirs(os.path.dirname(log_path), exist_ok=True)

enabled = True
time_str = '23:50'
timeframe = os.getenv('DEFAULT_TIMEFRAME', 'weekly')

if os.path.exists(settings_path):
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        cron_cfg = settings.get('cron', {})
        enabled = cron_cfg.get('enabled', True)
        time_str = cron_cfg.get('time', '23:50')
        timeframe = cron_cfg.get('timeframe', timeframe)
    except (json.JSONDecodeError, IOError) as e:
        print(f'Failed to read settings.json: {e}', flush=True)

if enabled and ":" in time_str:
    parts = time_str.split(":")
    hour = parts[0].zfill(2)
    minute = parts[1].zfill(2)
    cron_line = f"{minute} {hour} * * * cd /app && /usr/bin/python main.py >> {log_path} 2>&1"
else:
    # 無効時は空のcrontab（何も実行しない）
    cron_line = '# kakeibo-ai cron is disabled'

crontab_content = f'''# kakeibo-ai crontab (auto-generated from settings.json)
{cron_line}
# 空行が必要
'''

with open('/app/infra/docker/crontab', 'w') as f:
    f.write(crontab_content)

print(f'Crontab generated: enabled={enabled}, time={time_str}, timeframe={timeframe}', flush=True)
"

# crontabファイルを登録
crontab /app/infra/docker/crontab

echo "Starting cron daemon..."
# cronをフォアグラウンドで起動
cron -f
