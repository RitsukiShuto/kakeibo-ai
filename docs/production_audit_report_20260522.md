# Production Audit Report - 2026/05/22

## 概要
Issue #115 に基づき、本番環境（Raspberry Pi）の状態調査を実施しました。
コンテナは正常に稼働していますが、AI分析において **Google Gemini API の利用制限（429 RESOURCE_EXHAUSTED）** が発生しており、分析結果が生成されない状態であることを確認しました。

## コンテナ稼働状況
全ての主要コンテナが正常に動作しています。

| コンテナ名 | サービス | ステータス | 稼働時間 |
| :--- | :--- | :--- | :--- |
| kakeibo-api | backend | Up | 57 minutes |
| kakeibo-slack | slack | Up | 57 minutes |
| kakeibo-cron | cron | Up | 57 minutes |
| kakeibo-frontend | frontend | Up | 57 minutes |

## ログ分析
`slack` コンテナのログにて、AI分析実行時に以下のエラーが繰り返し発生していることを確認しました。

```
kakeibo-slack  | Starting AI Analysis (daily)...
kakeibo-slack  | AI analyzing 70 transactions and 4 asset categories...
kakeibo-slack  | AI Analysis error: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Your project has exceeded its monthly spending cap. Please go to AI Studio at https://ai.studio/spend to manage your project spend cap.'}}
```

**原因:**
Google AI Studio の月間利用枠（無料枠または設定された上限）を超過しています。

## 設定確認
`prod_local/.env` および `prod_local/config/settings.json` の設定内容を確認しました。

- **LLM_PROVIDER**: `gemini` (正)
- **active_model**: `gemini-pro-latest` (正)
- **GEMINI_API_KEY**: 設定済み
- **KAKEIBO_LOCAL_DIR**: 環境変数には設定されていませんが、Docker Compose のボリュームマウント (`./prod_local:/app/local`) とアプリケーションのデフォルト値 (`local`) が一致しているため、正しく `/app/local/kakeibo.db` や設定ファイルを読み込めています。

## リソース使用状況
Raspberry Pi のリソースには十分な余裕があります。

- **Disk**: 40% 使用 (34GB 空き)
- **Memory**: 約 2.5GB 利用可能 (Total 3.8GB)

## 提案事項・今後のアクション

1. **Gemini API の利用枠確認**:
   - Google AI Studio (https://aistudio.google.com/) にログインし、利用状況と上限設定を確認してください。
   - 無料枠を利用している場合、別のモデル（Gemini Flash等）への切り替え、または有料枠の検討が必要です。

2. **暫定対応: ローカルLLM (Ollama) への切り替え検討**:
   - Raspberry Pi 上で Ollama が動作可能であれば、`LLM_PROVIDER=ollama` に切り替えることで、コストをかけずに分析を継続できます。
   - ただし、Raspberry Pi 4 (4GB) では動作が非常に低速になる可能性があるため、検証が必要です。

3. **モデルの変更**:
   - `gemini-pro-latest` から `gemini-1.5-flash` などのより軽量でクォータの大きいモデルへの変更を検討してください。

4. **KAKEIBO_LOCAL_DIR の明示的設定 (推奨)**:
   - 混乱を避けるため、`prod_local/.env` に `KAKEIBO_LOCAL_DIR=local` を明示的に追加することを推奨します。

---
報告者: SRE Agent
調査日時: 2026年5月22日
