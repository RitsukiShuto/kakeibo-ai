import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# プロジェクトルートディレクトリを取得
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ログディレクトリの設定
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"

def setup_logger(name: str = "kakeibo-ai"):
    """
    標準化されたロガーをセットアップする。
    
    Args:
        name (str): ロガー名。
        
    Returns:
        logging.Logger: 設定済みのロガーインスタンス。
    """
    # ログディレクトリの作成
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    
    # 既にハンドラーが設定されている場合は、重複して追加しない
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # フォーマットの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # コンソール出力用ハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイル出力用ハンドラー (ローテーション設定)
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# デフォルトのロガーインスタンス
logger = setup_logger()
