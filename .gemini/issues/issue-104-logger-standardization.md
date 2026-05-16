# Issue: ログ出力の標準化 (Logger Standardization)

## 概要
現在、`src/` 配下の各モジュールでデバッグや進捗表示のために `print()` 関数が多用されています。これを Python 標準の `logging` モジュールを使用した共通ロガーに移行し、ログの管理性（レベル管理、ファイル出力、フォーマット統一）を向上させます。

## 背景
- `print()` ではエラーログと一般ログの区別が難しい。
- 実行ログをファイルに残す仕組みが不足しており、トラブルシューティングに支障が出る可能性がある。
- プロジェクト全体でログの出力形式が統一されていない。

## 完了定義 (Definition of Done)
- [x] `src/utils/logger.py` が作成され、標準的なロギング設定（コンソール、ファイル、ローテーション）が実装されている。
- [x] 主要なモジュール (`src/api/`, `src/analyzer/`, `src/output/`) の `print` が `logger` に置換されている。
- [x] `logs/` ディレクトリに実行ログが正しく保存されることを確認。
- [x] ローカルでのフルリグレッションテスト (`tools/run_regression.py`) をパスする。

## サブタスク
- [x] **Task 3.1: 共通ロガーの実装** (@backend-engineer)
    - `src/utils/logger.py` の作成。
    - `logs/app.log` への出力と、ファイルローテーションの設定。
- [x] **Task 3.2: APIサーバーの移行** (@backend-engineer)
    - `src/api/main.py` の `print` を `logger.info/error/debug` に変更。
- [x] **Task 3.3: 分析・DB・通知ロジックの移行** (@backend-engineer)
    - `src/analyzer/`, `src/db/`, `src/output/` 配下の `print` を置換。
- [x] **Task 3.4: メインエントリポイントの移行** (@backend-engineer)
    - `main.py` の `print` を置換。
- [x] **Task 3.5: 検証** (@qa-tester)
    - ログファイルが生成され、意図した形式で出力されているか確認。

## 優先的に移行すべきファイル
1. `src/api/main.py`
2. `src/analyzer/gemini_analyzer.py`
3. `main.py`
4. `src/output/slack_server.py`
5. `src/db/database.py`

## ステータス
- [x] 完了 (Closed)

## 完了コメント
プロジェクト全体のログ出力標準化を完了しました。`src/utils/logger.py` を通じて `logs/app.log` への永続化とコンソール出力の両立を実現しています。

