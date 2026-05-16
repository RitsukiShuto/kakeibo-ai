import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

from src.utils.logger import logger

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

class ObsidianWriter:
    def __init__(self):
        self.vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
        self.base_report_dir = "Reviews/Kakeibo"

        if not self.vault_path:
            logger.warning("OBSIDIAN_VAULT_PATH is not set. Saving to local 'reports' directory instead.")
            self.target_root = "reports/Reviews/Kakeibo"
        else:
            self.target_root = os.path.join(self.vault_path, self.base_report_dir)

    def write_report(self, content: str) -> str:
        """
        レポートを年月ごとのフォルダに整理して保存し、インデックスを更新
        """
        now = datetime.now()
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")
        
        # フォルダパス: target_root/2026/04/
        month_dir = os.path.join(self.target_root, year_str, month_str)
        os.makedirs(month_dir, exist_ok=True)

        filename = f"Kakeibo_Review_{now.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(month_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Report saved to: {filepath}")
            
            # インデックス（目次）を更新
            self._update_index(year_str, month_str, filename)
            
            return filepath
        except Exception as e:
            logger.error(f"Failed to save Obsidian report: {e}")
            return ""

    def _update_index(self, year: str, month: str, filename: str):
        """
        Kakeibo_Index.md に新しいレポートへのリンクを追記
        """
        index_path = os.path.join(self.target_root, "Kakeibo_Index.md")
        link_path = f"{year}/{month}/{filename}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = f"- [{timestamp}] [[{link_path}|家計簿レビュー ({timestamp})]]\n"

        try:
            # ファイルが存在しない場合はヘッダーを作成
            if not os.path.exists(index_path):
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write("# 📑 家計簿AIレビュー インデックス\n\n")
                    f.write("過去の分析レポート一覧です。リンクから詳細を確認できます。\n\n## 📝 レポート履歴\n")

            # 内容を追記
            with open(index_path, "a", encoding="utf-8") as f:
                f.write(new_entry)
            
            logger.info(f"Index updated: {index_path}")
        except Exception as e:
            logger.error(f"Failed to update Obsidian index: {e}")
