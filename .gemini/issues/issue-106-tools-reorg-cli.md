# Issue: Tools ディレクトリの整理と統合 CLI の開発 (Issue #106)

## 概要
現在 `tools/` ディレクトリ直下に多数の Python スクリプトが散在しており、管理が難しくなっています。これらを機能別にサブディレクトリへ整理し、一つのエントリポイントから呼び出せる統合 CLI を開発します。

## 背景
- スクリプトが増え、どれが何のためのものか把握しづらい。
- 各スクリプトで引数のパース方法やエラーハンドリングがバラバラ。
- `python tools/xxx.py` と直接叩くのではなく、`python tools/cli.py command` のような統一されたインターフェースが望ましい。

## 完了定義 (Definition of Done)
- [x] `tools/` 配下のスクリプトが `tools/db/`, `tools/analysis/`, `tools/fetch/`, `tools/maintenance/` 等に分類されている。
- [x] 統合 CLI (`tools/main.py` または `tools/cli.py`) が実装され、すべての主要機能をサブコマンドとして呼び出せる。
- [x] 既存の `scripts/` や GitHub Actions からの呼び出しが、新しいパス・コマンドに修正されている。
- [x] `qa-tester` による動作確認をパスする。
- [x] `security-reviewer` による監査をパスする。

## サブタスク
- [x] **Task 4.1: ディレクトリ構造の設計と移動** (@backend-engineer)
- [x] **Task 4.2: 統合 CLI フレームワーク (typer等) の導入と実装** (@backend-engineer)
- [x] **Task 4.3: 関連スクリプト (GitHub Actions, shell scripts) の修正** (@sre-deploy)
- [x] **Task 4.4: セキュリティ監査** (@security-reviewer)
- [x] **Task 4.5: 最終検証** (@qa-tester)

## ステータス
- [x] 完了 (Completed)
- [ ] 未着手 (Backlog)
- [ ] 進行中 (In Progress)

## 進捗メモ
- 2026-05-15: ディレクトリ整理と `typer` を用いた統合 CLI (`tools/cli.py`) の実装を完了しました。
- 2026-05-16: 関連スクリプトの修正、セキュリティ監査、およびリグレッションテストを完了し、全てのタスクをクローズしました。
