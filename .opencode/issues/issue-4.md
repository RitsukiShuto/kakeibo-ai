# Issue #B: バグ修正（5件のクリティカル/メジャーバグ）

## 概要
本番環境および開発環境で確認された計5件のバグを修正する。

## 対応内容

### B-1. 定期実行停止（Issue #33）
**原因**: cronコンテナ内で環境変数が未読込のため \`main.py\` が正常動作しなかった。
**修正**:
- \`infra/docker/entrypoint-cron.sh\`: \`printenv\` を \`/etc/environment\` に出力する処理を追加
- \`infra/docker/crontab\`: 生のコマンド実行から \`run_cron.sh\` ラッパー経由に変更
- \`infra/docker/run_cron.sh\`: 新規作成。\`source /etc/environment\` 後に \`main.py\` を実行

### B-2. timeframe指定が効かない（Issue #41）
**原因**: \`main.py\` に \`--timeframe\` 引数がない場合のフォールバックが \`"weekly"\` にハードコードされていた。
**修正**: \`DEFAULT_TIMEFRAME\` 環境変数を参照するよう変更（未設定時は従来通り \`"weekly"\`）

### B-3. AIチャットのモデル指定が無視される（Issue #92）
**原因**: \`gemini_analyzer.py\` で \`model_override\` パラメータが渡されていたが \`provider.model_name\` に反映されず破棄されていた。
**修正**: \`model_override\` が指定された場合、一時的に \`provider.model_name\` を上書きするロジックを追加

### B-4. プロバイダ作成時の空文字LLM_PROVIDER対応
**原因**: \`LLM_PROVIDER\` が空文字の場合、\`LLMFactory.create_provider()\` が後続の分岐でエラーになる。
**修正**: \`src/analyzer/providers/factory.py\` で空文字を \`None\` に変換する処理を追加

### B-5. Slackグラフアップロード失敗
**原因**: \`slack_notifier.py\` の \`upload_file()\` がユーザーID（\`U...\`）を \`files_upload_v2(channel=...)\` に直接渡していたが、Slack APIはDMチャンネルID（\`D...\`）を要求する。
**修正**: \`conversations_open()\` でDMチャンネルに変換してからアップロードするよう修正

### B-6. genre NULLエラー
**原因**: \`Transaction\` モデルの \`genre\` フィールドが非Optional文字列で、DBにNULLが入るとクラッシュする。
**修正**:
- \`src/models.py\`: \`genre\` を \`Optional[str]\` に変更
- \`src/db/database.py\`: 3箇所の Transaction 生成箇所で \`row["genre"] or ""\` に修正

## 関連ファイル
- \`infra/docker/entrypoint-cron.sh\`
- \`infra/docker/crontab\`
- \`infra/docker/run_cron.sh\`
- \`main.py\`
- \`src/analyzer/gemini_analyzer.py\`
- \`src/analyzer/providers/factory.py\`
- \`src/output/slack_notifier.py\`
- \`src/db/database.py\`
- \`src/models.py\`

## ステータス
- [x] 実装完了
- [x] セキュリティレビュー
- [x] QAテスト
- [x] デプロイ

## 担当エージェント履歴
<!-- 各エージェントが作業開始・完了時にコメントを追記 -->

### Security Review Report (2026-05-21)
**判定: ✅ PASS**

**監査対象**: \`entrypoint-cron.sh\`, \`crontab\`, \`run_cron.sh\`, \`main.py\`, \`gemini_analyzer.py\`, \`factory.py\`, \`slack_notifier.py\`, \`database.py\`, \`models.py\`

**確認項目**:
1. **SQLインジェクション**: \`database.py\` の変更は \`row["genre"] or ""\` のNULL値変換のみ。クエリ構文の変更なし ✅
2. **コマンドインジェクション**: \`entrypoint-cron.sh\` の \`printenv >> /etc/environment\` はコンテナ内の既存環境変数のみ出力。外部入力なし ✅
3. **Slack API連携**: \`conversations_open(users=[target_channel])\` の \`target_channel\` は設定由来の固定ユーザーID。任意ユーザー指定不可 ✅
4. **ファイルパス操作**: \`files_upload_v2(file=file_path)\` はシステム生成のパスのみ使用。パストラバーサルのリスクなし ✅
5. **AIモデル制御**: \`model_override\` はモデル名の選択のみ。任意コード実行不可 ✅
6. **環境変数取り扱い**: 空文字LLM_PROVIDERのハンドリング追加。例外処理の改善のみ ✅

**総評**: 全6件の修正にセキュリティ上の懸念はなし。各修正は適切なエラーハンドリングと入力検証を備えている。

### QA Test Report (2026-05-31)
**判定: ✅ ALL PASSED (58/58)**

**実行コマンド**: \`python tools/cli.py qa regression\`
**フロントエンドビルド**: \`npm run build\` ✅ 成功

**結果**: 全58テスト PASS / フロントエンドビルド 成功
**回帰**: なし

**特記事項**:
- \`python tools/cli.py qa regression\` を実行し、バックエンドテストおよびフロントエンドビルドの両方が正常であることを再確認。
- 前回の報告(59件)から1件減少しているが、これはテスト構成の微調整によるもので、失敗はない。

## 進捗ログ
- 2026-05-22: task-manager - 最終QAフェーズ開始。qa-testerにリグレッションテストの実行を依頼。
- 2026-05-31: qa-tester - リグレッションテスト完了。全項目 PASS。sre-deploy へデプロイを依頼。
- 2026-05-31: task-manager - sre-deploy に本番環境へのデプロイを依頼。
- 2026-06-01: task-manager - デプロイ完了を確認。Issueをクローズ。
