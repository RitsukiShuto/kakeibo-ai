import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from datetime import datetime
from typing import List
from src.db.database import Database

class Visualizer:
    def __init__(self, output_dir: str = "reports/graphs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # フォントに関する警告を抑制（OSにフォントがない場合でも動作を継続させる）
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning, message=".*Glyph.*missing from font.*")

        # 日本語フォント設定
        if os.name == 'nt': # Windows
            plt.rcParams['font.family'] = 'MS Gothic'
        else: # Linux/Raspberry Pi
            # 一般的な日本語フォントを優先順位順に指定
            jp_fonts = ['IPAexGothic', 'Noto Sans CJK JP', 'VL Gothic', 'DejaVu Sans']
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = jp_fonts

    def generate_asset_trend_graph(self, db_path: str = "local/kakeibo.db") -> str:
        """
        資産推移のグラフを生成し、保存したパスを返す
        """
        import sqlite3
        conn = sqlite3.connect(db_path)
        
        # 資産データを取得
        query = """
        SELECT acquired_date, asset_type, SUM(amount) as total_amount
        FROM assets
        GROUP BY acquired_date, asset_type
        ORDER BY acquired_date ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return ""

        df['acquired_date'] = pd.to_datetime(df['acquired_date'])
        
        # グラフ作成
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        # 積み上げエリアチャート
        pivot_df = df.pivot(index='acquired_date', columns='asset_type', values='total_amount').fillna(0)
        pivot_df.plot.area(ax=plt.gca(), alpha=0.7)
        
        plt.title("Asset Trend Analysis", fontsize=15)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Amount (JPY)", fontsize=12)
        plt.legend(title="Asset Type", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # 保存
        filename = f"asset_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path)
        plt.close()
        
        return save_path
