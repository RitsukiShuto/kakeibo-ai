#!/bin/bash

# Kakeibo AI Review System セットアップスクリプト
ENV_NAME="kakeibo-ai"

echo -e "\033[0;36m=== kakeibo_AI_ReviewSys セットアップを開始します ===\033[0m"

# 1. Conda環境の確認と作成
echo -e "\n\033[0;33m[1/4] Anaconda環境を構築しています...\033[0m"
if conda env list | grep -q "$ENV_NAME"; then
    echo "環境 '$ENV_NAME' は既に存在します。更新を確認します。"
    conda env update -n $ENV_NAME -f environment.yml
else
    conda env create -f environment.yml
fi

# 2. Playwrightのブラウザインストール
echo -e "\n\033[0;33m[2/4] Playwrightのブラウザをインストールしています...\033[0m"
conda run -n $ENV_NAME playwright install chromium

# 3. 環境設定ファイルの準備
echo -e "\n\033[0;33m[3/4] 環境設定ファイルを準備しています...\033[0m"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "\033[0;32m.env ファイルを作成しました。必要なAPIキーを設定してください。\033[0m"
else
    echo ".env ファイルは既に存在します。スキップします。"
fi

# 4. ディレクトリの作成
echo -e "\n\033[0;33m[4/4] 必要なディレクトリを作成しています...\033[0m"
mkdir -p data logs reports/Reviews/Kakeibo
echo "Directories created."

echo -e "\n\033[0;36m=== セットアップが完了しました！ ===\033[0m"
echo "1. '.env' ファイルを開き、GEMINI_API_KEY などを設定してください。"
echo "2. 'bash run.sh --no-headless' を実行して、MoneyForwardにログインしてください。"
