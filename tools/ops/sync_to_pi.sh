#!/bin/bash

# =================================================================
# Raspberry Pi 環境同期スクリプト (to Pi)
# ローカルの local/ ディレクトリを丸ごと Raspberry Pi へ転送します。
# =================================================================

# --- CONFIGURATION ---
PI_USER="r410"
PI_HOST="192.168.0.21"
PI_DIR="~/kakeibo-ai"
# ---------------------

echo -e "\033[0;36m=== Raspberry Pi への環境同期を開始します ===\033[0m"

if [ -d "local" ]; then
    echo "[1/1] local/ ディレクトリを転送中..."
    scp -r local ${PI_USER}@${PI_HOST}:${PI_DIR}/
else
    echo -e "\033[0;31mエラー: 'local' ディレクトリが見つかりません。\033[0m"
    exit 1
fi

echo -e "\n\033[0;36m=== 同期が完了しました！ ===\033[0m"
echo "ラズパイ側で 'python main.py' が正常に動作するか確認してください。"
