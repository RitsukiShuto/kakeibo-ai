# 📝 作業状況・引き継ぎ用 (CURRENT_TASK.md)

## 📅 更新日: 2026-05-14 (Updated)

## 🎯 現在の目標
- 準本番環境 (Staging) の自動運用化と本番データ同期の安全な確立。
- Web UI からのデータインポート機能の拡充。
- AI キャラクター切り替え機能の実装。

## 🚦 進捗状況
- [x] **Frontend**: ライフプラン画面の UI/UX 刷新 (2026-05-13)
- [x] **Infra**: ステージング環境のディレクトリ構成と Docker 設定の基礎構築 (2026-05-13)
- [x] **Deploy**: 最新の修正を本番環境 (Raspberry Pi) へデプロイ完了 (2026-05-13)
- [x] **Infra**: 開発環境における Ollama GPU 支援（NVIDIA Container Toolkit）の設定と検証 (2026-05-14)
- [ ] **Infra**: GitHub Actions による `staging` ブランチの自動デプロイ実装
- [ ] **Tool**: 本番 DB からステージングへの匿名化同期スクリプト (`sync_prod_to_staging.py`)
- [ ] **Backend**: CSV インポート API の実装
- [ ] **Frontend**: 設定画面での AI キャラクター選択機能

## 📌 完了した変更のサマリー
1. **UI/UX 刷新**: ライフプラン画面を 2 カラム化し、Markdown による AI アドバイス表示に対応。
2. **本番デプロイ**: SSH 経由での自動デプロイフローにより、最新のフロント/バックを本番環境へ反映。
3. **ステージング基盤**: `kakeibo-staging` プロジェクトとして本番と隔離された環境で Docker コンテナを起動可能にした。
4. **Ollama GPU 支援**: 開発環境の Ollama コンテナで GPU (NVIDIA) を利用可能にし、高速なローカル LLM 実行環境を構築。

## 💡 メモ
- ステージング環境（Port 8001/5174）が動作することを確認済み。
- 次の焦点は「いかに本番データを安全にステージングへ持ち込むか（匿名化）」と「GitHub Actions の拡張」。

---
## 📅 次のステップ: ステージングの自動化と機能拡張
1. **Automation**: `.github/workflows/ci-cd.yml` に `staging` 用のジョブを追加。
2. **Security**: `tools/sync_prod_to_staging.py` を作成し、個人情報（コメント等）をマスクして同期する。
3. **Feature**: フロントエンドの `Settings.tsx` を拡張し、AI キャラクターの切り替えと CSV アップロードを可能にする。
