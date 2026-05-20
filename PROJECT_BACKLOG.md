# 📋 Project Roadmap: Kakeibo AI Review System

> **💡 お知らせ**
> タスクおよびバックログの管理は **GitHub Issues** および **GitHub Projects** へ移行しました。
> 詳細なタスク（未完了・完了済）のトラッキングはリポジトリの Issues ページをご確認ください。

このドキュメントでは、プロジェクトの大きな方向性（ロードマップ）のみを管理します。

---

## 📅 ロードマップ
### Phase 0: 環境整備とリファクタリング (Done ✅)
- **本番環境仕様の整理**: `docs/PROD_ENV.md` の作成
- **トラブルシューティングガイドの作成**: `docs/TROUBLESHOOTING.md` の整備
- **ディレクトリ構造のリファクタリング**: `scripts/`, `tools/` への整理と統合 CLI (`tools/cli.py`) の開発によるレガシーファイルのアーカイブ化
- **開発ガイドラインの刷新**: `GEMINI.md` へのディレクトリ役割の追記

### Phase 1: 基盤構築とAI分析の導入 (Current)
- [x] WSL環境への移行と開発環境の再構築 (2026-05-13)
- [x] 本番環境 (Raspberry Pi) への公開鍵認証による SSH 接続確立 (2026-05-13)
- [x] 本番環境のシステム監査とドキュメント作成 (`docs/production_status.md`) (2026-05-13)
- [x] ステージング環境 (Staging) の基盤構築 (2026-05-14)
- [x] 開発環境における Ollama GPU 支援の設定と検証 (2026-05-14)
- [x] 準本番環境の自動デプロイとデータ同期 (CI/CD 拡張)
    - [x] GitHub Actions による `staging` ブランチの自動デプロイ設定 (gemini-1.5-flash)
    - [x] 匿名化機能付きデータ同期スクリプト (`tools/sync_prod_to_staging.py`) の開発
    - [x] ステージング環境での動作検証と品質確認
- [x] @data-analyst のプロンプト改善と実用性評価 (Issue #107) (2026-05-18)
- [x] Slackコマンドの検証と実機連携の確認 (Issue #108) (2026-05-18)
- [x] フロントエンド統合とデータ追加・削除機能の実装 (Issue #109) (2026-05-18)
- [x] STG環境の設定画面表示バグの修正 (Issue #112) (2026-05-17)
- [x] 手動インポート機能と初期設定UIの実装 (Issue #110) (2026-05-18)
- [x] マネーフォワード等の連携を通じたデータの自動取得
    - [x] MoneyForwardFetcherによるPlaywright自動取得（セッション管理・CSVパース・カテゴリマッピング）
    - [x] ZaimFetcherの用意
    - [x] CLI (main.py) からのデータ取得フロー確立
    - [x] Slackコマンド `/kakeibo-review` からのデータ取得トリガー
- [x] AIによる基本的な週次・月次レビューの生成
    - [x] KakeiboAnalyzerによるAI分析（daily/weekly/monthly/quarterly/yearly対応）
    - [x] ペルソナ切り替え機能（gal/butler/zen/default/sergeant）
    - [x] 複数モデル対応（Gemini Pro/Flash/Lite、Ollama）
    - [x] 立替金自動マッチング・解析機能
    - [x] カテゴリマッピングAI提案機能
- [x] Slack通知と簡単なオンデマンド実行
    - [x] Slack Block Kit によるリッチ通知（ととのい指数・ギャルコマンド付き）
    - [x] スラッシュコマンド実装（/kakeibo-review, /kakeibo-check, /kakeibo-model, /kakeibo-stats-ai, /kakeibo-last, /kakeibo-help）
    - [x] DM・メンションによるチャット応答機能
    - [x] ハートビート監視機能
- [x] Webダッシュボードのプロトタイプ構築
    - [x] React + TypeScript + Vite によるSPA実装
    - [x] 7ページ実装（Dashboard, Transactions, AIReview, AIChat, LifePlan, ExpenseSplitter, Settings）
    - [x] バックエンドAPI完全統合（KPI, 予算対実績, 取引CRUD, CSVインポート, 設定管理, AIチャット, ライフプラン, 立替検知）
    - [x] Axios APIクライアント実装

### Phase 2: 分析の高度化と予実管理の強化
- [x] 予算に対する支出推移の可視化
    - [x] `/api/budget-actual` エンドポイント実装
    - [x] フロントエンド Dashboard での予算対実績表示
- [x] AIによる特定カテゴリの深掘り分析と、具体的なアクション（ギャル・コマンド）の精度向上
    - [x] プロンプト改善（Issue #107）完了
- [x] スコア（ととのい指数）やアクション実績のDB記録・長期統計
    - [x] analysis_history テーブルによる分析履歴管理
    - [x] トークン使用量記録
    - [x] `/api/analysis-history` エンドポイント実装
- [x] 手動インポート機能と初期設定UIの実装 (Issue #110) (2026-05-18)
- [ ] AI キャラクターのパーソナライズ（設定画面での切り替え）
    - [x] バックエンド: `/api/settings/ai-models`, `/api/settings/active-persona` 実装済み
    - [ ] フロントエンド: Settings画面でのペルソナ切り替えUI改善（より直感的な操作感へ）

### Phase 3: ユーザー体験とインフラの向上
- [x] CI/CD パイプラインの完全統合（Staging 自動デプロイとテスト）
    - [x] GitHub Actions: validate → deploy-staging → deploy の3ステージ構成
    - [x] PR/マージ前のビルドチェック（pytest + npm build）
- [x] Dockerコンテナ化による環境構築の容易化
    - [x] docker-compose.yml / docker-compose.staging.yml 構成済み
    - [x] systemd サービス連携（tools/ops/setup_systemd.sh）
- [ ] レシートOCRや複数ユーザー対応など、入力の多様化
- [ ] 開発環境のさらなる改善（`scripts/dev.sh` の拡充）

### Phase 4: パーソナル・ファイナンス・エージェント化
- [x] ライフプランシミュレーション画面の刷新 (2026-05-13)
    - [x] LifePlanCalculator による資産推移シミュレーション
    - [x] `/api/life-plan/simulation`, `/api/life-plan/advice` エンドポイント
    - [x] フロントエンド LifePlan ページ実装
- [ ] ライフプランシミュレーションとの統合（AIアドバイスの改善）
- [ ] N年後のFIRE達成確率や住宅購入の妥当性に関する高度なアドバイス
- [ ] ユーザーの好みに応じたAIキャラクター（プロンプト）の選択機能
    - [x] 基盤実装済み（ペルソナ切り替え）
    - [ ] 更なるペルソナの追加とカスタマイズ性向上

---

## 🛠 今後の技術改善タスク (Next Steps)
- ~~**ブランチ整理と管理戦略の策定 (Issue #111)**~~: 完了済み
- **ツールの更なる細分化**: `tools/` 内のファイル数が多いため、`tools/db/`, `tools/analysis/`, `tools/dev/` 等へのサブカテゴリ化を検討。（※ 既に一部実施済み: `tools/import_data/`, `tools/ops/`, `tools/qa/` 等）
- ~~**セットアップ自動化の強化**~~: `scripts/setup.sh` に依存関係のバージョンチェック機能を追加。（※ `scripts/dev.sh` で対応済み）
- ~~**ログ出力の標準化**~~: `src/` 全体のログ出力を標準化し、`docs/TROUBLESHOOTING.md` との連携を強化。（Issue #104 で完了済み）
- **デプロイフローの堅牢化**: `scripts/sync_to_pi.sh` のエラーハンドリング強化と、デプロイ後のコンテナ状態チェックの自動化。
- **テストカバレッジの向上**: 現在1,393行のテストコード。フロントエンドのユニットテスト追加とE2Eテストの拡充。
- **セキュリティ強化**: `.env` のUI経由編集機能（実装済み）のセキュリティレビューと、セッション情報の安全な管理。

---

## 📊 コードレビューに基づく実装状況サマリー (2026-05-20 現在)

### 実装済み機能一覧
| 機能 | 状況 | 詳細 |
|------|------|------|
| MoneyForward自動取得 | ✅ 完了 | Playwright + セッション管理 + CSVパース + カテゴリマッピング |
| Zaim連携 | ✅ 完了 | ZaimFetcher実装済み |
| AI分析エンジン | ✅ 完了 | daily/weekly/monthly/quarterly/yearly + 5ペルソナ + 複数モデル |
| Slack連携 | ✅ 完了 | 6スラッシュコマンド + DMチャット + Block Kit通知 + ハートビート |
| Webダッシュボード | ✅ 完了 | 7ページ + API完全統合 + CRUD操作 |
| 立替金管理 | ✅ 完了 | 自動マッチング + AI検知 + 自然言語パーサー + ExpenseSplitter UI |
| CSVインポート | ✅ 完了 | バックエンドAPI + フロントエンドUI |
| 設定管理UI | ✅ 完了 | 環境変数・予算・プロファイル・マッピング・AIモデル/ペルソナ |
| ライフプラン | ✅ 完了 | シミュレーション計算 + AIアドバイス + UI |
| 予算対実績 | ✅ 完了 | API + Dashboard表示 |
| 分析履歴 | ✅ 完了 | DB記録 + トークン統計 + API |
| CI/CD | ✅ 完了 | 3ステージ（validate → staging → production）|
| Docker環境 | ✅ 完了 | compose + systemd連携 |
| テスト | ✅ 一部 | 17テストファイル（1,393行）、フロントエンドテスト未実装 |

### 未実装・改善余地あり
| 機能 | 状況 | 備考 |
|------|------|------|
| AIキャラクターのパーソナライズUI | 🟡 改善余地 | バックエンドは完成、Settings画面のUX改善が必要 |
| レシートOCR | ❌ 未着手 | 新機能として検討 |
| 複数ユーザー対応 | ❌ 未着手 | アーキテクチャ変更が必要 |
| フロントエンドユニットテスト | ❌ 未着手 | React Testing Library 等でのテスト追加 |
| FIRE達成確率計算 | ❌ 未着手 | ライフプラン拡張として検討 |
| デプロイフロー堅牢化 | 🟡 改善余地 | エラーハンドリング強化 |
