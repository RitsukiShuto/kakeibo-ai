# Issue 6: AI分析エンジンの責務分割とリファクタリング

## 概要
`src/analyzer/gemini_analyzer.py` の `KakeiboAnalyzer` クラスが多機能になりすぎているため、機能ごとに分割して保守性とLLMコンテキスト効率を向上させます。

## 分割案
- `base.py`: 基底クラス（プロンプト読込、ペルソナ管理）
- `review_analyzer.py`: 定期レビュー担当
- `assistant_analyzer.py`: 補助機能（立替、カテゴリ提案）担当
- `life_plan_analyzer.py`: ライフプラン担当
- `chat_agent.py`: チャット担当

## ステータス
- [ ] 計画策定
- [ ] 実装
- [ ] レビュー・検証

## 進捗ログ
- 2026-05-31: issue-proposer - 改善案として提案。正式にIssueとして起票。
