# Issue #113: CSV複数ファイルインポート対応

## 概要
現状のCSV手動インポート機能は1ファイルずつしかアップロードできないため、複数ファイルをまとめてアップロードできるように改修する。

## タスク内訳
- [x] **計画策定**: `task-manager` が実行計画を策定・Human承認済み
- [x] **API改修**: `backend-engineer` が `POST /api/import/csv` を複数ファイル対応に変更し、詳細な結果レスポンスを返す
- [x] **フロントエンド改修**: `frontend-engineer` が `<input type="file" multiple>` 対応、ファイルリスト表示、結果表示の改善
- [x] **セキュリティレビュー**: `security-reviewer` がファイルアップロードの脆弱性を監査（既存の一時ファイル処理・拡張子チェックを維持）
- [x] **QAテスト**: `qa-tester` がリグレッションテストを実施（58テスト全件PASS）
- [x] **デプロイ**: `sre-deploy` がPR作成

## 進捗ログ
- 2026-05-21: タスク起票。エージェントアサイン待ち。
- 2026-05-21: `backend-engineer` 完了。APIエンドポイントを複数ファイル対応に変更、`_process_single_csv` の戻り値を件数に変更。
- 2026-05-21: `frontend-engineer` 完了。複数ファイル選択UI、ファイルリスト表示、詳細な結果表示を追加。
- 2026-05-21: `security-reviewer` 合格。既存のセキュリティ対策を維持。
- 2026-05-21: `qa-tester` 合格。58テスト全件PASS、Frontend BuildもPASS。
- 2026-05-21: `sre-deploy` PR作成済み。
