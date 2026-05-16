# 準本番環境 (Staging Environment) 仕様書

準本番環境（以下、STG環境）は、本番環境へのデプロイ前に、本番と同等の構成で最終確認を行うための環境です。
Raspberry Pi 上で本番環境と並行して動作させることを想定しています。

## 1. コンセプト
- **完全隔離**: 本番環境のプロセス、ネットワーク、データと干渉しないこと。
- **環境再現**: 本番環境と同一の Docker イメージ、構成ファイルを使用すること。
- **安全なデータ検証**: 本番データのコピーを使用してテストできるが、本番データを書き換えないこと。

## 2. インフラ構成 (Isolation)

STG環境は、Docker Compose のプロジェクト機能を使い、コンテナ名やネットワークを分離します。

| 項目 | 本番環境 (PROD) | 準本番環境 (STG) | 備考 |
| :--- | :--- | :--- | :--- |
| **プロジェクト名** | `kakeibo-ai` (デフォルト) | `kakeibo-staging` | `-p kakeibo-staging` で指定 |
| **Frontend ポート** | `5173` | `5174` | `http://[IP]:5174` でアクセス |
| **Backend ポート** | `8000` | `8001` | |
| **コンテナ名 prefix** | `kakeibo-*` | `kakeibo-staging-*` | |

## 3. データとボリューム (Storage)

データの混同を防ぐため、マウントするホストディレクトリを分離します。

| ホストパス | 本番環境 (PROD) | 準本番環境 (STG) |
| :--- | :--- | :--- |
| 設定・DB | `./local` | `./staging/local` |
| ログ | `./logs` | `./staging/logs` |
| データ入力 | `./data` | `./staging/data` |
| レポート出力 | `./reports` | `./staging/reports` |

## 4. 環境変数と設定

STG環境専用の `.env` ファイルを使用します。

- ファイルパス: `staging/local/.env`
- 主な変更点:
  - `DB_PATH=/app/local/kakeibo_staging.db`
  - `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN`: 可能であれば検証用 Bot を使用（本番用と共通でも Socket Mode なら別プロセスで動作可能だが、誤爆防止のため分離推奨）。
  - `IS_STAGING=true` (環境識別用フラグ)

## 5. 運用フロー

### A. 環境構築
1. ディレクトリの作成: `mkdir -p staging/local staging/logs staging/data staging/reports`
2. 設定のコピー: `cp local/.env staging/local/.env` (必要に応じて編集)
3. 起動: `docker compose -f docker-compose.staging.yml up -d`

### B. 本番データの同期 (検証時)
本番の SQLite DB をコピーして STG環境で動作確認する場合の手順：
```bash
cp local/kakeibo.db staging/local/kakeibo_staging.db
```

### C. デプロイ検証
`staging` ブランチにプッシュすると、GitHub Actions により Raspberry Pi の `/home/r410/kakeibo-staging` ディレクトリに自動デプロイされます。

デプロイ後は以下のコマンドで状態を確認できます（Raspberry Pi上）：
```bash
cd /home/r410/kakeibo-staging
docker compose -f docker-compose.staging.yml ps
docker compose -f docker-compose.staging.yml logs backend --tail 50
```

## 6. CI/CD 設定の詳細
`.github/workflows/ci-cd.yml` に `deploy-staging` ジョブが定義されています。
- トリガー: `staging` ブランチへのプッシュ
- デプロイ先: `/home/r410/kakeibo-staging`
- 使用ファイル: `docker-compose.staging.yml`
- 自動設定: `ACTIVE_MODEL=gemini-1.5-flash` によるコスト最適化

## 7. 今後の課題
- 自動リグレッションテスト (`tools/run_regression.py`) の STG環境での実行。
- データの匿名化スクリプトの検討（個人情報保護が必要な場合）。
