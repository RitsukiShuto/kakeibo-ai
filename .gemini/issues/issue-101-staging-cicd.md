# Issue: ステージング環境用 CI/CD パイプラインの実装

## 概要
`staging` ブランチへのプッシュをトリガーとして、Raspberry Pi 上のステージング環境へ自動デプロイする GitHub Actions ワークフローを構築する。

## 作業内容
- [x] `.github/workflows/ci-cd.yml` を編集し、`staging` ブランチ用のジョブを追加した。
- [x] `docker-compose.staging.yml` を使用して、Raspberry Pi 上の `staging/` ディレクトリへデプロイするフローを確立。
- [x] ステージング環境の `settings.json` にて、`gemini-1.5-flash` をデフォルトモデルに設定し、コスト削減を実現。

## 担当エージェント
- @sre-deploy

## ステータス
- [x] 完了 (Closed)

## 完了コメント
`staging` ブランチへの push により、Raspberry Pi 上の `/home/r410/src/kakeibo-ai/staging/` 配下への自動デプロイが正常に動作することを確認しました。また、環境変数および設定ファイルを通じて、低コストモデルの利用設定を完了しました。
