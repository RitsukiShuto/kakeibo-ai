# AI家計簿レビューシステム 全体開発計画 (最終案)

## 1. プロジェクト概要
家計簿サービス（Zaim）からデータを自動取得し、AIによる高度なデータ分析（データサイエンティスト型）を実行する。その詳細な分析結果をObsidian（Markdown形式）に蓄積しつつ、Slackへ要約を定期通知する完全自動化の個人向けシステムを構築する。
運用コストを最小化するため、ユーザー手持ちのRaspberry Piをサーバーとして活用し、Pythonによるバッチ処理システムとして稼働させる。

## 2. システムアーキテクチャ

```mermaid
graph TD
    subgraph Raspberry Pi (Local / Python)
        Cron[Cron / スケジューラ] --> Fetcher
        Fetcher[データ取得モジュール]
        Analyzer[AI分析モジュール]
        Output[出力モジュール]
        
        Fetcher --> |取得データ| Analyzer
        Analyzer --> |分析結果| Output
    end
    
    Zaim[Zaim API] --> Fetcher
    Analyzer <--> |APIリクエスト| AI[AI API: Gemini等]
    Output --> |Webhook| Slack[Slack通知]
    Output --> |Markdown出力| Obsidian[Obsidian (ローカル/同期)]
```

## 3. 主要コンポーネントと技術スタック

- **実行環境:** Raspberry Pi (Linux)
- **開発言語:** Python 3.x
- **データ取得元:** Zaim (公式APIを使用)
- **AI分析 (データサイエンティスト型):** Google Gemini API (無料枠・低コスト運用に最適)
- **通知先:** Slack (Incoming Webhooks)
- **データ蓄積先:** Obsidian (ローカルMarkdown出力)

## 4. 開発フェーズとマイルストーン

### Phase 1: データ取得モジュールの開発
- Zaim API 連携のセットアップ
- 家計簿データ（収支明細）の自動取得機能の実装
- データのクレンジングと保存

### Phase 2: AI分析モジュールの開発
- AI プロンプトエンジニアリング
- 過去データ比較や傾向分析ロジックの実装

### Phase 3: 出力・通知モジュールの開発
- Slack 通知、Obsidian 出力機能

### Phase 4: 自動化設定
- Cron 設定、ロギング、エラー監視
