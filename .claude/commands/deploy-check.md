ローカルおよびリモート環境のDockerサービス稼働状況を確認し、日本語でレポートします。

以下の手順で確認してください：

1. **ローカル開発環境のチェック**（実行可能な場合）：
   ```bash
   docker compose -f docker-compose.dev.yml ps
   docker compose -f docker-compose.dev.yml logs --tail 30
   ```

2. **GitHub Actions の最新実行状況**：
   ```bash
   gh run list --limit 5
   ```
   最新のCI/CDパイプラインのステータスを確認する。

3. **ブランチとデプロイ状況**：
   ```bash
   git log --oneline -5 origin/staging
   git log --oneline -5 origin/main
   ```

4. **リモート環境（Raspberry Pi）の確認**：
   直接SSH接続はできないため、ユーザに以下のコマンド実行を案内する：
   ```bash
   # 本番環境
   ssh r410@<raspberry-pi-ip> 'cd kakeibo-ai && docker compose ps && docker compose logs backend --tail 20'
   # ステージング環境
   ssh r410@<raspberry-pi-ip> 'cd STG_kakeibo-ai && docker compose ps && docker compose logs backend --tail 20'
   ```

出力フォーマット（日本語）：
```
## デプロイ状況レポート

| 環境 | ステータス | 備考 |
|---|---|---|
| ローカル (dev) | ✅ 稼働中 / ❌ 停止 | ... |
| CI/CD | ✅ 成功 / ❌ 失敗 | 最新run: #xxx |
| staging | 確認待ち | ... |
| production | 確認待ち | ... |
```
