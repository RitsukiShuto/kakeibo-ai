# Kakeibo AI Review System — Claude Code ガイド

家計簿データのAI分析・管理システム。FastAPI バックエンド + React/TypeScript フロントエンド + Slack ボット + Raspberry Pi デプロイ構成。

---

## 技術スタック

| レイヤ | 技術 |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend | React 18, TypeScript, Vite, Recharts |
| AI | Google Gemini API / Ollama (Local LLM) |
| Infra | Docker Compose, GitHub Actions CI/CD, Raspberry Pi |
| データ取得 | Playwright (MoneyForward自動取得), Zaim |

## ディレクトリ構成

| ディレクトリ | 役割 |
|---|---|
| `src/` | コアロジック — `analyzer/`, `api/`, `db/`, `fetcher/` |
| `frontend/` | React SPA (`frontend/src/components/`, `pages/`) |
| `tools/` | CLI ユーティリティ (`python tools/cli.py <category> <cmd>`) |
| `scripts/` | セットアップ・運用スクリプト |
| `local/` | ローカル開発環境 — `.env`, DB, `config/settings.json` |
| `dev_local/` | 開発用 Docker 環境 |
| `prod_local/` | **本番専用ファイル（触れない）** |
| `docs/` | 環境仕様・トラブルシューティング |

---

## 開発フロー

### ブランチ戦略（厳守）
```
feature/* or fix/*  →  staging  →  main
```
- `main` / `staging` への直接コミット禁止（PR 経由のみ）
- マージ完了後、作業ブランチを即削除

### PR作成前に必須
```bash
python tools/cli.py qa regression   # バックエンドテスト + フロントエンドビルド
```
これをパスしていない PR はマージされない。

### 環境の分離（重要）
- `prod_local/` からのコードPull・変更同期は**絶対禁止**
- 開発は `dev_local/` 環境で完結させ、Git経由でデプロイ

---

## テスト戦略

| ティア | タイミング | コマンド |
|---|---|---|
| Tier 1 (単体) | 開発中・随時 | `pytest tests/test_xxx.py -v` |
| Tier 2 (フル) | PR作成前 | `python tools/cli.py qa regression` |
| Tier 3 (CI) | Push時 | GitHub Actions 自動実行 |

`tests/conftest.py` により、テスト実行時はAI APIが自動モック化される。費用なし、何度でも実行可。

---

## よく使うコマンド

```bash
# ローカル開発環境
bash scripts/dev.sh up          # 環境起動
bash scripts/dev.sh down        # 環境停止
bash scripts/dev.sh logs        # ログ表示
bash scripts/dev.sh test        # コンテナ内テスト

# データ操作
python tools/cli.py fetch history
python tools/cli.py qa regression

# フロントエンド
cd frontend && npm run build    # ビルド検証
cd frontend && npm run dev      # 開発サーバ起動
```

---

## スキル一覧（Claude Code スラッシュコマンド）

| コマンド | 用途 |
|---|---|
| `/qa` | フルリグレッション実行・結果レポート |
| `/propose` | バックログ分析・次タスク提案 |
| `/deploy-check` | Docker コンテナ稼働確認 |
| `/new-feature <name>` | TDDフローで新機能開発開始 |
| `/security-audit` | 変更ファイルのセキュリティ監査 |

---

## サブエージェント設計

Claude Code で複雑なタスクを委任するときは `Agent` ツールを使う。
専門エージェントのプロンプトテンプレートは `.claude/agents/` 配下に格納。

| 役割 | ファイル |
|---|---|
| バックエンド実装 | `.claude/agents/backend-engineer.md` |
| フロントエンド実装 | `.claude/agents/frontend-engineer.md` |
| セキュリティ監査 | `.claude/agents/security-reviewer.md` |
| QAテスト | `.claude/agents/qa-tester.md` |
| SREデプロイ | `.claude/agents/sre-deploy.md` |

---

## 共通ルール

- ユーザへの応答は**必ず日本語**（コードコメント・変数名は英語可）
- セキュリティレビューなしの PR 作成禁止
- `python tools/cli.py qa regression` パスなしの PR 作成禁止
- 実装前に必ずテストを書く（TDD）
- 計画はユーザの承認を得てから実装に移行する
