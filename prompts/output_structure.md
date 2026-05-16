## 出力形式定義 (JSON Schema)

以下のJSONスキーマに従って、純粋なJSONオブジェクトのみを出力してください。
Markdownのコードブロック（```json）は含めないでください。
全ての項目を必ず埋めてください。

```json
{
  "slack_report": "Slack用の詳細レポート本文（Markdown/絵文字を駆使したレポート。※あとの'actions'セクションと重複するため、具体的なアクションリストはここには含めないでください）",
  "obsidian_report": "Obsidian用のMarkdown形式の詳細レポート全文（Calloutやアクションリストも含めて、1つの完結した記事として作成してください）",
  "actions": [
    {
      "command": "Now/Keep/Stopなどの短いコマンド",
      "description": "具体的なアクション内容"
    }
  ],
  "asset_breakdown": [
    {
      "category": "資産カテゴリ名",
      "amount": 10000
    }
  ],
  "budget_status": [
    {
      "category": "食費",
      "budget": 40000,
      "actual": 42000,
      "status": "超過"
    }
  ],
  "totonoi_score": "0-100の整数",
  "savings_potential": "今月あといくら節約できるかの概算額（整数）"
}
```

## レポート作成ガイドライン
- **Obsidian Callout:** `obsidian_report` では Obsidian で管理しやすいよう、Callout形式（`> [!INFO]`, `> [!WARNING]`, `> [!TIP]` など）を積極的に活用してください。
- **Slack フルレポート:** `slack_report` では、Slack の Mrkdwn 形式を厳守してください。
    - **太字:** `*テキスト*` （`**` は使用不可）
    - **章立て:** Slack は `#` や `###` の見出しをサポートしていないため、章立ては `*■ 章タイトル*` のように太字と記号を組み合わせて表現してください。
    - **リスト:** `•` や `*` を使用し、項目ごとに改行してください。
    - 絵文字を適度に使用して、明るく読みやすいレイアウトにしてください。
- **構造化:** 視認性を高めるため、セクション間に空行を挟んでください。
