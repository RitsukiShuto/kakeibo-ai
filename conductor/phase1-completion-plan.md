# Plan: 次のステップの起票とPhase 1の完了に向けた計画

## Objective
Issue #107の完了処理を行い、ユーザーからの追加要望を反映した新しいIssue（#108, #109, #110）を起票する。その後、直近で優先度の高いタスクの実行準備を整える。

## ユーザーからの追加要望
- **Issue #109**: フロントエンドダッシュボードにて、データの追加・削除機能も実装する。
- **Issue #110**: 手動インポート機能に加え、`mf_session`などの初期設定もUIから行えるようにする。

## Tasks
1. **バックログの更新 (`PROJECT_BACKLOG.md`)**
   - Issue #107 (@data-analyst プロンプト改善) を「完了」に更新する。
   - Issue #108, #109 を Phase 1 のタスクとして追記する。
   - Issue #110 を Phase 2 のタスクとして追記する。

2. **Issueファイルの起票 (`.gemini/issues/`)**
   - `issue-108-slack-command-verification.md` を作成する（Slack連携検証）。
   - `issue-109-frontend-api-integration.md` を作成する（フロントエンド統合、データ追加・削除要件を含む）。
   - `issue-110-ui-manual-import-setup.md` を作成する（手動インポート機能、初期設定要件を含む）。

3. **次タスクの着手**
   - 上記の管理タスク完了後、まずは直近で必要となる Issue #108 または #109 の設計・実装タスクに移行する。

## Verification & Testing
- `PROJECT_BACKLOG.md` の目視確認。
- `.gemini/issues/` に正しい要件を含んだマークダウンファイルが生成されていること。
