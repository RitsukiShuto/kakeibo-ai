# Issue 6: AI分析エンジンの責務分割とリファクタリング

## 概要
\`src/analyzer/gemini_analyzer.py\` の \`KakeiboAnalyzer\` クラスが多機能になりすぎているため、機能ごとに分割して保守性とLLMコンテキスト効率を向上させます。

## 対応内容
- \`base.py\`: 基底クラス（プロンプト読込、ペルソナ管理）の抽出
- \`review_analyzer.py\`: 定期レビュー担当 (analyze_kakeibo) の分離
- \`assistant_analyzer.py\`: 補助機能（立替、カテゴリ提案）担当の分離
- \`life_plan_analyzer.py\`: ライフプラン担当の分離
- \`chat_agent.py\`: チャット担当の分離
- \`gemini_analyzer.py\`: 移譲（Composition）による既存コードへの互換性維持

## ステータス
- [x] 計画策定
- [x] 実装
- [x] レビュー・検証

## 進捗ログ
- 2026-05-31: issue-proposer - 改善案として提案。正式にIssueとして起票。
- 2026-06-01: task-manager - 責務分割の実装完了。リグレッションテスト (62 passed) により動作を確認。
