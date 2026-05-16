# 実行計画: ステージング環境の高度化とCI/CD構築

ユーザーより承認された「Raspberry Pi上へのステージング環境構築」プランに基づき、コスト削減とデータ分離の要件を追加して実行します。

## 1. 目標
- `staging` ブランチへのプッシュによる自動デプロイを実現する。
- ステージング環境では低コストなAIモデル（`gemini-1.5-flash`）をデフォルトで使用する。
- 本番データを匿名化して安全にステージング環境へ同期する仕組みを構築する。

## 2. タスク分割と Issue 管理

### Issue #101: CI/CD Expansion (@sre-deploy)
- **内容**: `.github/workflows/ci-cd.yml` の拡張。
- **追加要件**: 
    - ステージング環境（`staging/` ディレクトリ）へのデプロイフロー構築。
    - 環境変数で `gemini-1.5-flash` をデフォルトに設定。

### Issue #102: Data Anonymization Sync Script (@backend-engineer)
- **内容**: `tools/sync_prod_to_staging.py` の作成。
- **追加要件**:
    - 本番DBの保護（書き込み禁止チェック）。
    - データの匿名化（店舗名・メモのハッシュ化/伏せ字化）。

### Issue #103: Staging Verification (@qa-tester)
- **内容**: ステージング環境でのエンドツーエンドテスト。
- **要件**:
    - デプロイ後のAPI疎通確認。
    - AI分析が指定の低コストモデルで行われているかの確認。

## 3. 進行状況
- [x] 実行計画の策定とIssue更新
- [ ] Task 1.1: CI/CD実装 (@sre-deploy) - **NEXT**
- [ ] Task 1.2: データ同期スクリプト実装 (@backend-engineer)
- [ ] Task 1.3: 検証 (@qa-tester)

## 4. ハンドオフ
- タスク管理エージェントより `agent-manager` へ、Issue #101 のアサインを依頼します。
