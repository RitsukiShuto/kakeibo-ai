# Issue #A: dev環境の本番同等化

## 概要
開発環境（Docker Compose dev）を本番環境と同等の構成にし、Local LLM（Ollama）を用いてコストゼロで動作検証できるようにする。

## 対応内容

### 1. docker-compose.dev.yml の拡充
- Slackサービス（slack_server.py）を追加
- Cronサービス（main.py定期実行）を追加
- Ollama連携設定（`OLLAMA_BASE_URL`, `LLM_PROVIDER=ollama`）
- `network_mode: "host"` によりホストマシンのOllamaに直接アクセス

### 2. Slackコマンドのdev対応
- `src/output/slack_server.py` に `/dev-` プレフィックス対応を追加
  - 正規表現 `re.compile(r"^/(dev-)?kakeibo-...$")` で本番/開発両対応
- dev用Slackアプリからのコマンドを正しくハンドリング

### 3. dev環境設定の完全化
- `dev_local/.env` に本番同等の環境変数を設定
  - `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_USER_ID`
  - `GEMINI_API_KEY`（開発用APIキー）
  - `DASHBOARD_URL=http://localhost`
  - `OBSIDIAN_VAULT_PATH`
  - `DEFAULT_TIMEFRAME=daily`

## 関連ファイル
- `docker-compose.dev.yml`
- `src/output/slack_server.py`
- `dev_local/.env`
- `dev_local/config/settings.json`

## ステータス
- [x] 実装完了
- [ ] セキュリティレビュー
- [ ] QAテスト
- [ ] デプロイ

## 担当エージェント履歴
<!-- 各エージェントが作業開始・完了時にコメントを追記 -->

### Security Review Report (2026-05-21)
**判定: ✅ PASS**

**監査対象**: `docker-compose.dev.yml`, `src/output/slack_server.py`, `dev_local/.env`

**確認項目**:
1. **シークレット管理**: `dev_local/.env` に Slackトークン・Gemini APIキーを含む。`.gitignore` で `dev_local/` が除外済みであることを確認 ✅
2. **Slackコマンド処理**: 正規表現 `^/(dev-)?kakeibo-...$` は固定パターンのコマンドマッチングに使用。任意ユーザー入力の評価なし ✅
3. **Docker構成**: `network_mode: "host"` はdev環境限定。本番同等の分離性は維持 ✅

**総評**: セキュリティ上の懸念はなし。dev環境限定の設定であり、本番環境への影響もない。

### QA Test Report (2026-05-21)
**判定: ✅ ALL PASSED (59/59)**

**実行コマンド**: `docker compose -f docker-compose.dev.yml exec backend pytest tests/ -v`
**フロントエンドビルド**: `docker compose -f docker-compose.dev.yml build frontend` ✅ 成功

**結果**: 全59テスト PASS / フロントエンドビルド 成功
**回帰**: なし

**備考**: テストは `test_dashboard_e2e.py` の `DASHBOARD_URL` 環境変数対応を含む全テストが通過。`pytest.mark.e2e` の未登録警告が1件あるが、E2Eテストの実行自体に影響なし。
