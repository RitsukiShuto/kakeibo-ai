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

## 期待される結果
- 個々のファイルサイズが小さくなり、将来の改修時にAIエージェントのコンテキスト消費を抑えることができる。
- 可読性が向上し、保守性が高まる。
- アプリケーションの動作（機能）に変更はないこと（リファクタリングのみ）。

## 作業手順 (Execution Plan)

1. **`src/api/main.py` のリファクタリング (バックエンド)**
   - `src/api/routers/` ディレクトリの作成
   - 各ルーターモジュールの作成とエンドポイントの移行
   - `main.py` の修正
   - `pytest` を実行し、既存のテストがパスすることを確認
2. **`Settings.tsx` のリファクタリング (フロントエンド)**
   - `frontend/src/components/settings/` ディレクトリの作成
   - サブコンポーネントへの分割
   - `Settings.tsx` の修正
   - `npm run build` でビルドが通ることを確認
3. **QA/レビュー**
   - リグレッションテスト (`python tools/cli.py qa regression`) の実行
   - ローカルでの動作確認（設定画面が正しく表示されるか、保存できるか）

