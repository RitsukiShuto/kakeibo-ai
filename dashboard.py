import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
from src.db.database import Database

# ページ設定
st.set_page_config(page_title="Kakeibo AI Dashboard", page_icon="💰", layout="wide")

# データベース接続
DB_PATH = "data/kakeibo.db"
db = Database(db_path=DB_PATH)

def load_budget():
    budget_path = "config/budget.json"
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def render_dashboard_content(timeframe):
    col_left, col_right = st.columns([1, 2])

    # --- 左側カラム: 分析＆履歴 ---
    with col_left:
        # 1. AIレビュー履歴
        st.subheader("🤖 AI Analysis History")
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT created_at, timeframe, score, summary, report_path FROM analysis_history WHERE timeframe = '{timeframe}' ORDER BY created_at DESC"
        df_hist = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_hist.empty:
            # 最新のレビューを大きく表示
            latest = df_hist.iloc[0]
            st.info(f"**Latest Summary ({latest['created_at']})**\n\n{latest['summary']}")
            with st.expander("View Full Report"):
                if latest['report_path'] and os.path.exists(latest['report_path']):
                    with open(latest['report_path'], "r", encoding="utf-8") as f:
                        st.markdown(f.read())
                else:
                    st.caption("詳細レポートが見つかりません。")
            
            # 過去の履歴をリスト化
            if len(df_hist) > 1:
                st.write("**Previous Reviews**")
                for index, row in df_hist.iloc[1:5].iterrows():
                    with st.expander(f"{row['created_at']} (Score: {row['score']})"):
                        st.write(row['summary'])
        else:
            st.info(f"{timeframe} の分析履歴がありません。")

        st.divider()

        # 2. 最近の明細
        st.subheader("📝 Recent Transactions")
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT transaction_date, category, amount, comment FROM transactions ORDER BY transaction_date DESC LIMIT 20"
        df_tx = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_tx.empty:
            st.dataframe(df_tx, use_container_width=True, height=300)
        else:
            st.caption("取引データがありません。")

    # --- 右側カラム: 可視化＆予実 ---
    with col_right:
        # 3. 資産推移
        st.subheader("📈 Asset Trend Analysis")
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT acquired_date, asset_type, SUM(amount) as total_amount
        FROM assets
        GROUP BY acquired_date, asset_type
        ORDER BY acquired_date ASC
        """
        df_assets = pd.read_sql_query(query, conn)
        conn.close()

        if not df_assets.empty:
            df_assets['acquired_date'] = pd.to_datetime(df_assets['acquired_date'])
            pivot_df = df_assets.pivot(index='acquired_date', columns='asset_type', values='total_amount').fillna(0)
            st.area_chart(pivot_df, height=350)
            
            # 合計推移（ミニチャート）
            total_growth = pivot_df.sum(axis=1)
            st.caption("Total Asset Growth")
            st.line_chart(total_growth, height=150)
        else:
            st.warning("資産データが見つかりません。")

        st.divider()

        # 4. 予実管理
        st.subheader("⚖️ Budget vs Actual")
        budget = load_budget()
        
        if budget:
            monthly_budget = budget.get("monthly", {})
            budget_categories = monthly_budget.get("categories", {})
            
            # 今月のデータを取得
            current_month = datetime.now().strftime("%Y-%m")
            conn = sqlite3.connect(DB_PATH)
            query = f"SELECT category, SUM(amount) as actual FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment' GROUP BY category"
            df_actual = pd.read_sql_query(query, conn)
            conn.close()
            
            # メトリクス表示
            total_budget = sum(budget_categories.values())
            total_actual = df_actual['actual'].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Budget", f"{total_budget:,}円")
            m2.metric("Actual", f"{total_actual:,}円", delta=f"{total_budget-total_actual:,}円", delta_color="inverse")
            m3.metric("Remaining", f"{max(0, total_budget-total_actual):,}円")

            # カテゴリ別プログレス
            st.write("**Category Progress**")
            cols = st.columns(2)
            for i, (cat, b_amt) in enumerate(budget_categories.items()):
                actual_row = df_actual[df_actual['category'] == cat]
                a_amt = int(actual_row['actual'].iloc[0]) if not actual_row.empty else 0
                progress = min(a_amt / b_amt, 1.0) if b_amt > 0 else 0
                status_color = "red" if a_amt > b_amt else "green"
                
                with cols[i % 2]:
                    st.write(f"{cat}: {a_amt:,} / {b_amt:,}")
                    st.progress(progress)
        else:
            st.info("`config/budget.json` が設定されていません。")

st.title("📊 Kakeibo AI Integrated Dashboard")

# トップタブによる集計期間の切り替え
timeframe_list = ["weekly", "monthly", "quarterly", "yearly"]
tabs = st.tabs([tf.capitalize() for tf in timeframe_list])

for i, tab in enumerate(tabs):
    with tab:
        render_dashboard_content(timeframe_list[i])

st.sidebar.markdown("---")
st.sidebar.caption("Kakeibo AI Review System v1.2")
if st.sidebar.button("Refresh Data"):
    st.rerun()
