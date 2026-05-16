# Kakeibo AI Review System - 開発ガイドライン

## 🤖 エージェントチーム運用 (Autonomous Agent Team)
本プロジェクトでは、メインエージェントが「リード・オーケストレーター」として動作し、サブエージェント（`.gemini/agents/`）を自律的に指揮します。

### 連携ルール
1. **自動アサイン**: 複雑な変更（DB変更を伴う機能追加など）の場合、メインエージェントは各専門エージェントにタスクを分割して依頼してください。
2. **TDD (Test-Driven Development) の徹底**: すべての実装はテストを先に書く TDD 方式で進めます。バックエンド実装時や検証時には、実装の進捗に合わせて都度テスト設計を見直してください。
3. **作業フローの遵守**: すべてのエージェントは `.gemini/WORKFLOW.md` に定義された標準作業手順（SOP）に従ってください。
4. **セキュリティ第一**: バックエンド・フロントエンドの実装完了ごとに、必ず `security-reviewer` による監査を受けてください。
5. **継続的検証**: 実装（backend/frontend）の後は、必ず `qa-tester` を通じて `python tools/cli.py qa regression` を実行し、品質を担保してください。
6. **環境の分離 (重要)**: **本番環境（Raspberry Pi等）からソースコードをPullしたり、変更を同期したりすることは絶対に禁止です。** 本番環境特有のファイル（`prod_local/`）があるため、開発環境との競合やCIの失敗を招く恐れがあります。開発は必ずローカルの `dev_local/` 環境で完結させ、Git経由でデプロイしてください。

## 﨟槫柏 テスト戦略 (Quality First)

品質と開発速度を両立させるため、以下のテスト戦略を徹底します。品質の最終責任は **「ローカル環境でのフルリグレッション」** が持ちます。

### 1. ティア構成

| ティア | レベル | 実行タイミング | 実行内容 | 目的 |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | 単体 | 開発中（随時） | 関連する `pytest` | モジュール単位の即時検証 |
| **Tier 2** | フル | **PR作成/マージ前** | `python tools/cli.py qa regression` | 全体への影響とビルド成否の確認 |
| **Tier 3** | CI | プッシュ時 | GitHub Actions | 最小限の型チェックとデプロイ可否判定 |

### 2. ローカル・フルリグレッションの実行

PR を作成する前、および `main` ブランチにマージする前には、必ず以下のコマンドをローカル環境で実行し、すべてのチェックが **PASS** することを確認してください。

```bash
python tools/cli.py qa regression
```

このスクリプトは以下の項目を自動で検証します。
- **Backend**: 全ユニットテスト（AI API は自動でモック化されます。費用はかかりません）。
- **Frontend**: `npm run build` による TypeScript の型チェックとビルド検証。

### 3. AI モックの仕組み

`tests/conftest.py` により、テスト実行時は Gemini API への通信が自動的に遮断され、ダミーレスポンスに差し替えられます。
- 費用を気にせず何度でもテストを回してください。
- 実機（Gemini）での挙動を確認したい場合は、個別のテストファイルでモックを解除するか、手動テストを行ってください。

### 4. プルリクエストのルール

本プロジェクトでは、コードの安全性を担保するため、以下のブランチ戦略を徹底します。

1. **作業ブランチ (`feature/*`, `fix/*`)**: 各機能開発やバグ修正を行います。
2. **`staging` ブランチ**: 準本番環境への反映用。作業ブランチからの PR はまずここへマージします。Raspberry Pi 上のステージング環境で動作確認を行います。
3. **`main` ブランチ**: 本番環境。`staging` での検証完了後、`staging` から `main` への PR を作成し、マージすることで本番デプロイが実行されます。

PR の説明欄には、必ず **「`python tools/cli.py qa regression` をパスした旨（またはその出力）」** を記載してください。これをパスしていない PR はマージされません。

---

## 﨟槫勠 Raspberry Pi へのデプロイ

- **`staging` にマージされると**: GitHub Actions が自動的に Raspberry Pi のステージング環境 (`/home/r410/STG_kakeibo-ai`) へデプロイします。
- **`main` にマージされると**: GitHub Actions が自動的に Raspberry Pi の本番環境 (`/home/r410/kakeibo-ai`) へデプロイを開始します。

デプロイ後は以下のコマンドでサービスの健康状態を確認してください。

```bash
docker compose ps
docker compose logs backend --tail 50
```

---

## 📂 ディレクトリ構成と役割

プロジェクトの整合性を維持するため、以下の構成に従ってファイルを配置してください。

| ディレクトリ | 役割 | 主な内容 |
| :--- | :--- | :--- |
| `src/` | **コアロジック** | バックエンド API, 分析エンジン, DB 操作, データ取得 |
| `frontend/` | **Web UI** | React (Vite) によるダッシュボード実装 |
| `scripts/` | **自動化・設定** | システムセットアップ (`setup.sh`), 実行補助 (`run.sh`) |
| `tools/` | **ユーティリティ** | データインポート, 手動分析, リグレッションテスト |
| `docs/` | **ドキュメント** | 本番環境仕様 (`PROD_ENV.md`), トラブルシューティング (`TROUBLESHOOTING.md`) |
| `infra/` | **インフラ構成** | Docker, Nginx, Systemd の設定ファイル |
| `local/` | **ローカル環境** | 環境変数 (`.env`), ローカル DB, 設定ファイル |

### スクリプトの実行方法
開発や運用のためのスクリプトを実行する際は、プロジェクトのルートディレクトリから以下の形式で実行してください。

- **Python ツール (推奨)**: `python tools/cli.py <category> <command>` (例: `python tools/cli.py fetch history`)
- **シェルスクリプト**: `bash scripts/xxx.sh` (例: `bash scripts/setup.sh`)

---

## 💻 ローカル開発環境 (Local Development)

本プロジェクトでは、Docker を使用して本番同様の環境をローカルで再現できます。また、コスト削減のため、開発中は **Local LLM (Ollama)** を利用することを推奨します。

### 1. セットアップと起動

初回、または設定を初期化したい場合は以下のコマンドを実行してください。

```bash
# 設定の初期化と LLM モデルのプル (対話形式)
bash scripts/dev.sh setup

# 環境の起動 (API, Frontend, Ollama)
bash scripts/dev.sh up
```

### 2. 環境の管理

| コマンド | 内容 |
| :--- | :--- |
| `bash scripts/dev.sh up` | 環境を起動します |
| `bash scripts/dev.sh down` | 環境を停止します |
| `bash scripts/dev.sh logs` | コンテナのログを表示します |
| `bash scripts/dev.sh test` | コンテナ内でバックエンドテストを実行します |

### 3. LLM の切り替え

`local/.env` の `LLM_PROVIDER` を書き換えることで、利用する AI を切り替えられます。
- `ollama`: ローカルの AI モデルを使用 (無料・高速)
- `gemini`: Google Gemini API を使用 (高精度・有料)

モデルの詳細は `local/config/settings.json` の `active_model` で指定してください。
