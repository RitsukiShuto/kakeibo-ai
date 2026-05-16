# トラブルシューティングガイド

本システムの運用中に発生する可能性のある問題とその対処法をまとめています。

## 1. ログの確認方法

コンテナが正常に動作していない場合は、まずログを確認してください。

```bash
# 全サービスのログを表示
docker compose logs -f

# 特定のサービスのログを表示
docker compose logs -f backend
docker compose logs -f slack
docker compose logs -f cron
```

## 2. サービスの再起動

設定の変更を反映させたい場合や、動作が不安定な場合は再起動を試してください。

```bash
# 全サービスを再起動
docker compose restart

# 特定のサービスのみ再起動
docker compose restart frontend
```

## 3. よくある問題と対処法

### 3.1. ポートが既に使用されている
**症状**: `docker compose up` 時に `Address already in use` エラーが発生する。
- **対処**: 5173番ポート（Frontend）または 8000番ポート（Backend）が他のプロセスで使用されていないか確認してください。
- **確認コマンド**: `sudo lsof -i :5173`

### 3.2. 権限エラー
**症状**: ログに `Permission denied` と表示され、ファイルが書き込めない。
- **対処**: ホスト側の `local/`, `logs/`, `data/`, `reports/` ディレクトリに書き込み権限があるか確認してください。
- **コマンド**: `sudo chmod -R 777 ./logs ./reports ./data ./local` (開発/デバッグ用)

### 3.3. API 接続エラー
**症状**: ダッシュボードにデータが表示されない、または Slack コマンドが反応しない。
- **対処**:
    - `local/.env` のトークンが正しいか確認してください。
    - `backend` コンテナが起動しているか確認してください (`docker compose ps`)。
    - ブラウザのデベロッパーツールで API リクエスト (`/api/status` 等) が 502 Bad Gateway になっていないか確認してください。

### 3.4. マネーフォワード取得失敗 (Playwright)
**症状**: `cron` サービスでマネーフォワードの取得が失敗する。
- **対処**:
    - セッションが切れている可能性があります。PC側で `python tools/cli.py fetch setup-session` を実行し、新しい `local/mf_session` を Raspberry Pi へ転送してください。
    - Raspberry Pi がメモリ不足に陥っている可能性があります。スワップ領域を増やすことを検討してください。

### 3.5. データベースのロック
**症状**: `database is locked` エラーが発生する。
- **対処**: SQLite は同時書き込みに弱いため、大量のデータを一度に処理している際に発生することがあります。しばらく待ってから再試行してください。

## 4. クリーンアップ

環境を初期化したい場合（**注意: データが消えます**）。

```bash
# コンテナとイメージの削除
docker compose down --rmi all

# データベースのリセット (必要な場合のみ)
rm local/kakeibo.db
```
