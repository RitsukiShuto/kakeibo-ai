#!/bin/bash

# Raspberry Pi 専用セットアップスクリプト
# scripts/ ディレクトリからルートディレクトリへ移動
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# ---------------------------------------------------------
ENV_NAME="kakeibo-ai"
PYTHON_VERSION="3.10"

echo -e "\033[0;36m=== Raspberry Pi Setup for kakeibo_AI_ReviewSys ===\033[0m"

# 1. OSアーキテクチャの確認
ARCH=$(uname -m)
echo -e "\033[0;33m[Check] Architecture: $ARCH\033[0m"
if [[ "$ARCH" != "aarch64" ]]; then
    echo -e "\033[0;31mWarning: 32bit環境（armv7l等）を検出しました。\033[0m"
    echo "Playwrightは64bit OS（aarch64）を推奨しています。"
fi

# 2. システムパッケージの更新とインストール（※パスワードが必要なため、失敗した場合は手動で実行してください）
echo -e "\n\033[0;33m[1/5] システムパッケージを確認中...\033[0m"
echo "If this step fails due to sudo password, please run the following manually:"
echo "sudo apt update && sudo apt install -y git wget curl build-essential libgbm-dev libasound2 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libpango-1.0-0 libcairo2 libasound2 libpangocairo-1.0-0"

# 3. Minicondaのインストール
if ! command -v conda &> /dev/null; then
    echo -e "\n\033[0;33m[2/5] Minicondaをインストール中...\033[0m"
    if [[ "$ARCH" == "aarch64" ]]; then
        WGET_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
    else
        WGET_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-armv7l.sh"
    fi

    wget $WGET_URL -O miniconda_installer.sh
    bash miniconda_installer.sh -b -p $HOME/miniconda3
    rm miniconda_installer.sh

    # パスの反映
    export PATH="$HOME/miniconda3/bin:$PATH"
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda init bash
else
    echo -e "\n\033[0;32m[2/5] Minicondaは既にインストールされています。\033[0m"
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
fi

# 4. Conda環境の作成
echo -e "\n\033[0;33m[3/5] Conda環境 '$ENV_NAME' を作成・更新中...\033[0m"
if conda env list | grep -q "$ENV_NAME"; then
    conda env update -n $ENV_NAME -f environment.yml
else
    # 修正: environment.yml から直接作成
    conda env create -n $ENV_NAME -f environment.yml
fi

# 5. Playwrightのセットアップ
echo -e "\n\033[0;33m[4/5] Playwrightのブラウザと依存関係をインストール中...\033[0m"
conda run -n $ENV_NAME pip install playwright
conda run -n $ENV_NAME playwright install chromium
conda run -n $ENV_NAME playwright install-deps chromium

# 6. 環境設定の準備
echo -e "\n\033[0;33m[5/5] プロジェクトディレクトリを整理中...\033[0m"
mkdir -p data logs reports/Reviews/Kakeibo

echo -e "\n\033[0;36m=== セットアップ完了！ ===\033[0m"
