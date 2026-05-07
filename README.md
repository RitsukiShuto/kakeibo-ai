# 🍓 Kakeibo AI Review System (v1.1.0)

マネーフォワードME や Zaim から最新の家計簿データを自動取得し、最新の **Gemini 3.1 Pro Preview**（AIデータサイエンティスト「ギャル」）が詳細な分析レポートと改善アクションを提案するシステムです。
Raspberry Piでの完全自動運用（CI/CDデプロイ対応）を想定していますが、ローカル端末(Windows/Mac)でも動作します。

---

## 💡 主な特徴と新機能
- **🚀 Slack オンデマンド実行:** Slackのコマンド（`/review`）からいつでも分析をキックできます。急いでいる時は `/review monthly skip` でデータ取得をスキップして爆速実行も可能。
- **🤝 AI Expense Splitter (立替金管理):** 飲み会などの立替を「純粋な支出」から分離して管理。AIによる自然言語解析での分割設定、入金明細との自動マッチングによる精算、週次レビューでのリマインドに対応。
- **📈 現実的な着地予測:** 単純な日割り計算を排除し、過去の傾向や固定費を加味した高度な「月末着地予測」を実装。
- **🎯 アクション管理:** Slackに届く「ギャル・コマンド（改善提案）」の「やったよ！✨」ボタンを押すことで、インタラクティブにモチベーションを維持できます。
- **📊 マルチ出力対応:** 詳細レポートを Obsidian (Markdown) へ自動保存し、要約を Slack へ通知。さらに `Streamlit` によるWebダッシュボードでグラフや履歴を確認可能。
- **⚙️ CI/CD 自動デプロイ:** GitHub Actions に統合され、メインブランチへプッシュすると「テスト実行 ➜ 成功時のみ Raspberry Pi へ自動デプロイ ➜ Slackへ完了通知」という一連のパイプラインが稼働します。

---

## 🛠 セットアップ (Anaconda環境)

### 1. 仮想環境の作成と有効化
```bash
conda env create -f environment.yml
conda activate kakeibo-ai
```

### 2. ブラウザエンジン (Playwright) のインストール
```bash
python -m playwright install chromium
```

### 3. 環境変数の設定 (`local/.env`)
プロジェクトルートの `.env.example` を `local/.env` にコピーし（`setup.sh`/`setup.ps1`を実行すれば自動で行われます）、以下の情報を入力してください。
- `MF_USER_ID` / `MF_PASSWORD`: マネーフォワードのログイン情報
- `GEMINI_API_KEY`: Google Gemini APIキー
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN`: Slackアプリ用のトークン（Bot権限とSocket Mode用）
- `SLACK_USER_ID`: 通知を送るあなた個人のSlack User ID
- `OBSIDIAN_VAULT_PATH`: ObsidianのVault（保管庫）のフルパス

---

## 🚀 使い方

### パターンA: 手動・定期実行 (CLI)
Cron等で自動実行させる場合の基本コマンドです。
```bash
# マネーフォワードのデータを元に、週次レビューを実行する
python main.py --source mf --timeframe weekly

# データ取得をスキップして、過去データで月次レビューのみ再実行する
python main.py --source mf --timeframe monthly --skip-fetch
```

### パターンB: Slack連携サーバーの起動
裏側でサーバーを立ち上げておくことで、スマホのSlackアプリからいつでも操作できるようになります。
```bash
python src/output/slack_server.py
```
> Slack側で `/review` または `/review monthly` と送信してください。

### パターンC: Webダッシュボードの起動
ブラウザで資産推移グラフや最新のレポートを確認できます。
```bash
streamlit run dashboard.py
```

---

## 📂 ディレクトリ構造
- `src/fetcher/`: 家計簿データのスクレイピング・API取得（MoneyForward, Zaim）
- `src/analyzer/`: Gemini API を活用したデータ分析・プロンプトエンジン
- `src/output/`: 各種プラットフォームへの出力（Slack, Obsidian, Visualizer）
- `src/db/`: データベース管理（SQLite）
- `tests/`: ユニットテスト群（pytest）
- `.github/workflows/`: CI/CDパイプライン (`ci-cd.yml`)
- `docs/`: Raspberry Pi 構築ガイド等のドキュメント
