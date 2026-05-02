# AI家計簿レビューシステム (MoneyForward版)

マネーフォワードMEから最新の家計簿データを自動取得し、Gemini API（AIデータサイエンティスト）が詳細な分析レポートを作成するシステムです。
Raspberry Piでの自動運用を想定していますが、ローカル端末(Windows/Mac)でも動作します。

## 💡 特徴
- **2フェーズ実行:** 「データ取得」と「AI分析」を分離し、デバッグやプロンプト調整が容易。
- **自動セットアップモード:** 初回のみブラウザを表示して2段階認証をサポート。2回目以降は完全自動実行。
- **最新データ重視:** 取得直前にマネフォの「一括更新」を実行し、銀行・カードの最新明細を反映。
- **マルチ出力:** 詳細レポートを Obsidian (Markdown) へ保存し、要約を Slack へ通知。

## 🛠 セットアップ (Anaconda)

### 1. 仮想環境の作成と有効化
```bash
# 環境の作成
conda env create -f environment.yml

# 環境の有効化
conda activate kakeibo-ai
```

### 2. ブラウザのインストール
```bash
python -m playwright install chromium
```

### 3. 環境変数の設定
`.env.example` を `.env` にリネームし、以下の情報を入力してください。
- `MF_USER_ID`: マネーフォワードのメールアドレス
- `MF_PASSWORD`: マネーフォワードのパスワード
- `GEMINI_API_KEY`: Google Gemini APIキー
- `SLACK_WEBHOOK_URL`: Slackの Incoming Webhook URL
- `OBSIDIAN_VAULT_PATH`: ObsidianのVault（保管庫）のフルパス

### 4. 初回ログイン (Setup)
```bash
python prepare_input.py
```
初回のみブラウザが立ち上がります。手動でログインと2段階認証を完了させてください。
成功すると `config/settings.json` が更新され、次回から自動実行（画面なし）になります。

## 🚀 使い方

### Step 1: データの取得
```bash
python prepare_input.py
```
マネーフォワードから最新明細を取得し、 `input_data.json` を作成します。

### Step 2: AI分析の実行
```bash
python run_analysis.py
```
`input_data.json` を読み込み、AI分析レポートを生成して Obsidian/Slack へ出力します。

## 📂 ディレクトリ構造
- `src/fetcher/`: データ取得（MoneyForward, Zaim）
- `src/analyzer/`: AI分析（Gemini プロンプト設計）
- `src/output/`: 出力処理（Slack, Obsidian）
- `config/`: システム設定・状態管理
- `docs/`: 設計ドキュメント類
- `input_data.json`: 一時保存される家計簿データ（AIへのインプット）
