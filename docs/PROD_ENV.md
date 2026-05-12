# 本番環境仕様書 (Production Environment)

本システムは Docker Compose を使用してコンテナ化されており、Raspberry Pi 等の Linux 環境での動作を想定しています。

## 1. サービス構成

システムは以下の 4 つのマイクロサービスで構成されています。

| サービス名 | コンテナ名 | 役割 | 実行コマンド |
| :--- | :--- | :--- | :--- |
| **slack** | `kakeibo-slack` | Slack Bot サーバー (Socket Mode) | `python src/output/slack_server.py` |
| **backend** | `kakeibo-api` | FastAPI によるバックエンド API | `python src/api/main.py` |
| **frontend** | `kakeibo-frontend` | React フロントエンド + Nginx プロキシ | `nginx -g 'daemon off;'` |
| **cron** | `kakeibo-cron` | 定期実行タスク (マネーフォワード取得等) | `/app/infra/docker/entrypoint-cron.sh` |

## 2. ネットワークとポート

フロントエンドの Nginx がリバースプロキシとして動作し、API へのリクエストをバックエンドコンテナに転送します。

| ホストポート | コンテナポート | サービス | 説明 |
| :--- | :--- | :--- | :--- |
| `5173` | `80` | `frontend` | Web ダッシュボード (Nginx) |
| `8000` | `8000` | `backend` | API サーバー (FastAPI) |

### Nginx プロキシ設定 (`/api/`)
`frontend` コンテナの Nginx は、`/api/*` へのリクエストを `http://backend:8000/*` へプロキシします。

## 3. ボリュームマウント (データの永続化)

以下のディレクトリはホストマシンと同期され、コンテナの再起動後もデータが保持されます。

| ホストパス | コンテナパス | 内容 |
| :--- | :--- | :--- |
| `./local` | `/app/local` | 設定ファイル (`.env`, `config/*.json`), SQLite DB (`kakeibo.db`), セッション情報 |
| `./logs` | `/app/logs` | 実行ログ |
| `./data` | `/app/data` | インポート用 CSV データ等 |
| `./reports` | `/app/reports` | 生成された分析レポート (Markdown, Graphs) |

## 4. 環境変数

設定は `local/.env` に集約されています。主要な変数は以下の通りです。
- `SLACK_BOT_TOKEN`: Slack Bot の API トークン
- `SLACK_APP_TOKEN`: Slack App Level トークン (Socket Mode 用)
- `GEMINI_API_KEY`: Google Gemini API キー
- `DB_PATH`: SQLite データベースのパス (通常は `/app/local/kakeibo.db`)

## 5. Docker イメージの詳細

- **Backend/Slack/Cron**: `mcr.microsoft.com/playwright/python:v1.43.0-jammy` ベース
    - Python 3.10+ と Playwright (Chromium) がインストール済み。
- **Frontend**: `nginx:stable-alpine` ベース
    - React アプリがビルドされ、`/usr/share/nginx/html` に配置されています。
