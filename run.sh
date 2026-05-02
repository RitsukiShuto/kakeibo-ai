#!/bin/bash

# 設定: Anacondaのパス（環境に合わせて調整が必要な場合があります）
CONDA_PATH=$(which conda)
ENV_NAME="kakeibo-ai"

echo "=== Kakeibo AI Review System Task Started: $(date) ==="

# 仮想環境で実行
if [ -z "$CONDA_PATH" ]; then
    echo "Error: conda not found. Please ensure Anaconda/Miniconda is installed."
    exit 1
fi

# 引数がある場合はそのまま渡し、ない場合は自動判定に任せる
conda run -n $ENV_NAME python main.py "$@"

echo "=== Task Completed: $(date) ==="
