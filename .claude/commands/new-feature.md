TDDフローに沿って新機能の開発を開始します。

使い方: `/new-feature <feature-name>`

引数が指定されていない場合は、機能名をユーザに確認してください。

## 実行手順

### Step 1: ブランチ作成
```bash
git checkout -b feature/<feature-name>
```

### Step 2: 要件の確認
以下をユーザに確認する（簡潔に）：
- この機能が解決する問題
- 対象のファイル・モジュール（src/ or frontend/）
- 完了条件（何ができたら「完成」か）

### Step 3: TDD 計画の策定
ユーザの承認を得てから実装に入る。計画には以下を含める：
- 追加・変更するファイル一覧
- **テストケース一覧（先に書く）**
- 実装アプローチの概要

### Step 4: テストファースト実装
1. `tests/` 配下にテストファイルを作成（失敗する状態）
2. `pytest tests/test_<feature>.py -v` で失敗を確認
3. 実装して全テストをGREENにする
4. フロントエンドが絡む場合は `cd frontend && npm run build` で確認

### Step 5: フルQA
```bash
python tools/cli.py qa regression
```
PASSED になってからPR作成へ進む。

### Step 6: PR作成
- ターゲットブランチ: `staging`（`main`ではない）
- PR説明に「`python tools/cli.py qa regression` をパスした旨」を記載

進捗はすべて日本語で報告すること。
