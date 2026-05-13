#!/bin/bash

# プロジェクトのディレクトリに移動 (cronでの相対パスエラー防止)
# scripts/ ディレクトリからルートディレクトリへ移動
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# 設定: Anaconda/Minicondaのインストール先
# 環境に合わせて優先順位順に探索します
CONDA_LOCATIONS=(
    "$HOME/miniconda3"
    "$HOME/anaconda3"
    "/home/r410/miniconda3"
    "/usr/local/miniconda3"
)

CONDA_BASE=""
for loc in "${CONDA_LOCATIONS[@]}"; do
    if [ -d "$loc" ]; then
        CONDA_BASE="$loc"
        break
    fi
done

# 見つからない場合はPATHにあるcondaを使用
if [ -z "$CONDA_BASE" ]; then
    CONDA_BASE=$(conda info --base 2>/dev/null)
fi

ENV_NAME="kakeibo-ai"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/execution_$(date +%Y%m%d).log"
mkdir -p "$LOG_DIR"

{
    echo "--------------------------------------------------"
    echo "Task Started: $(date)"
    echo "Project Dir: $PROJECT_ROOT"
    
    # 実行環境のベースディレクトリ判定
    if [ -z "$KAKEIBO_LOCAL_DIR" ]; then
        if [ -d "$PROJECT_ROOT/prod_local" ]; then
            export KAKEIBO_LOCAL_DIR="prod_local"
        elif [ -d "$PROJECT_ROOT/dev_local" ]; then
            export KAKEIBO_LOCAL_DIR="dev_local"
        else
            export KAKEIBO_LOCAL_DIR="local"
        fi
        echo "Using base directory: $KAKEIBO_LOCAL_DIR"
    fi

    if [ -z "$CONDA_BASE" ]; then
        echo "Error: Conda not found. Please set CONDA_BASE in run.sh."
        exit 1
    fi

    # Conda環境の初期化
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate "$ENV_NAME"

    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate conda environment '$ENV_NAME'."
        exit 1
    fi

    # 引数がある場合はそのまま渡し、ない場合は自動判定に任せる
    # PYTHONPATHをプロジェクトルートに設定
    export PYTHONPATH="$PROJECT_ROOT"
    python main.py "$@"

    echo "Task Completed: $(date)"
    echo "--------------------------------------------------"
} 2>&1 | tee -a "$LOG_FILE"
