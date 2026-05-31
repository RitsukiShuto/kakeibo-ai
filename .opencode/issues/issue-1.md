# Issue 1: コンテキストサイズの削減とコード分割（リファクタリング）

## 概要
現在のプロジェクトは機能が充実してきた一方で、一部のファイル（特にフロントエンドの `Settings.tsx` とバックエンドの `src/api/main.py`）が肥大化し、LLMエージェントが読み込む際のコンテキストサイズが大きくなっています。
これを削減するため、ファイルを適切に分割するリファクタリングを行います。

## 対象ファイルと分割方針

### 1. `frontend/src/pages/Settings.tsx` (約1,350行)
このファイルは様々な設定UIを一つにまとめているため肥大化しています。設定項目ごとにコンポーネントを分割します。

- `frontend/src/components/settings/` ディレクトリを作成
- 以下のコンポーネントに分割:
  - `GeneralSettings.tsx` (予算、プロフィールなど)
  - `AISettings.tsx` (AIモデル、ペルソナなど)
  - `CategoryMappingSettings.tsx` (カテゴリマッピング)
  - `SystemSettings.tsx` (環境変数、Cron設定など)
- `Settings.tsx` はこれらのコンポーネントをまとめるラッパーとタブUIのみにする

### 2. `src/api/main.py` (約1,080行)
FastAPIのエンドポイントが全て一つのファイルに記述されています。機能（ルーター）ごとに分割します。

- `src/api/routers/` ディレクトリを作成
- 以下のモジュールに分割し、`APIRouter` を使用してルーティングする:
  - `transactions.py` (取引関連: `/api/transactions`, `/api/import/csv`)
  - `analysis.py` (分析・KPI関連: `/api/kpi`, `/api/budget-actual`, `/api/analysis-history`)
  - `settings.py` (設定関連: `/api/settings/*`)
  - `ai.py` (AI機能関連: `/api/chat`, `/api/life-plan/*`, `/api/expense-splitter/*`)
- `main.py` は各ルーターを `app.include_router()` で読み込む役割と、CORS設定などの初期化に留める

## ステータス
- [x] バックエンド分割 (`main.py` -> `routers/`)
- [x] フロントエンド分割 (`Settings.tsx` -> `components/settings/`)
- [x] 品質検証 (`qa regression` PASS)
- [x] クローズ

## 進捗ログ
- 2026-05-31: task-manager - リファクタリング作業の開始。
- 2026-05-31: backend-engineer - `src/api/main.py` を `utils.py` および `routers/` (dashboard, transactions, settings, analysis, reimbursements) に分割。
- 2026-05-31: frontend-engineer - `Settings.tsx` を `components/settings/` 配下の7つのサブコンポーネントに分割。
- 2026-05-31: qa-tester - リグレッションテストを実行。全58テスト PASS およびフロントエンドビルド成功を確認。
- 2026-05-31: task-manager - ユーザーによる動作確認完了。Issueをクローズ。

