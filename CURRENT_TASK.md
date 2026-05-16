# 実行計画: Phase 1 の完遂とツールの整理 (Task 4)

## 1. 目標
Phase 1 の主要機能を統合・検証し、散在するツール群を整理して保守性の高い CLI 基盤を構築する。

## 2. 完了済みのタスク (Verified & Ready for Deploy)

### Task 1: データ取得 (Fetch) 機能の API 化と UI 実装
- [x] **Task 1.1: Fetch API の実装 (@backend-engineer)**
- [x] **Task 1.2: フロントエンドへの「更新ボタン」追加 (@frontend-engineer)**

### Task 2: オンデマンド AI レビュー機能の実装
- [x] **Task 2.1: レビュー生成 API の実装 (@backend-engineer)**
- [x] **Task 2.2: AI レビュー画面のブラッシュアップ (@frontend-engineer)**

### Task 3: ログ出力の標準化
- [x] **Task 3.1: 共通ロガーの実装 (@backend-engineer)**
- [x] **Task 3.2: 主要モジュールのリファクタリング (@backend-engineer)**
- [x] **Task 3.3: ログ出力の検証 (@qa-tester)**

## 3. 現在進行中のタスク

### Task 4: Tools ディレクトリの整理と統合 CLI の開発 (Issue #106)
- [ ] **Task 4.1: ディレクトリ構造の設計と移動 (@backend-engineer)**
    - `tools/` 配下のスクリプトを機能別に整理。
- [ ] **Task 4.2: 統合 CLI の実装 (@backend-engineer)**
    - `python tools/cli.py` を通じた統一インターフェースの提供。
- [ ] **Task 4.3: 関連設定・スクリプトの修正 (@sre-deploy)**
    - GitHub Actions や `scripts/` 内のパス参照を更新。
- [ ] **Task 4.4: セキュリティ・品質検証 (@security-reviewer, @qa-tester)**
    - 整理後のツール群が正常に動作し、機密情報を適切に扱うことを確認。

## 4. 成功基準
- `python tools/cli.py --help` で利用可能な全機能が一覧表示されること。
- 既存の自動化スクリプトや CI が正常に動作すること。
- `tools/` ディレクトリが整理され、新規ツールの追加場所が明確であること。
