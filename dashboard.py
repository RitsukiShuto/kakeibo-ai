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

st.title("📊 Kakeibo AI Review Dashboard")

# サイドバー設定
st.sidebar.header("Settings")
timeframe_option = st.sidebar.selectbox("Analysis Timeframe", ["weekly", "monthly", "quarterly", "yearly"])

# タブの作成
tab1, tab2, tab3, tab4 = st.tabs(["📈 資産推移", "⚖️ 予実管理", "📝 最近の明細", "🤖 AIレビュー履歴"])

with tab1:
    st.header("Asset Trend Analysis")
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
        st.area_chart(pivot_df)
        
        # 合計推移
        st.subheader("Total Asset Growth")
        total_growth = pivot_df.sum(axis=1)
        st.line_chart(total_growth)
    else:
        st.warning("資産データが見つかりません。")

with tab2:
    st.header("Budget vs Actual (予実管理)")
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
        
        # 予実データの突合
        budget_data = []
        for cat, b_amt in budget_categories.items():
            actual_row = df_actual[df_actual['category'] == cat]
            a_amt = int(actual_row['actual'].iloc[0]) if not actual_row.empty else 0
            diff = b_amt - a_amt
            status = "✅ OK" if diff >= 0 else "🚨 Over"
            progress = min(a_amt / b_amt, 1.0) if b_amt > 0 else 0
            
            budget_data.append({
                "Category": cat,
                "Budget": b_amt,
                "Actual": a_amt,
                "Remaining": diff,
                "Status": status,
                "Progress": progress
            })
        
        df_budget_view = pd.DataFrame(budget_data)
        
        # メトリクス表示
        total_budget = sum(budget_categories.values())
        total_actual = df_actual['actual'].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Budget", f"{total_budget:,}円")
        col2.metric("Total Actual", f"{total_actual:,}円", delta=f"{total_budget-total_actual:,}円")
        col3.metric("Savings Goal", f"{monthly_budget.get('savings_goal', 0):,}円")

        # 進捗バー付きテーブル
        st.subheader("Category Breakdown")
        for index, row in df_budget_view.iterrows():
            col_a, col_b = st.columns([1, 4])
            col_a.write(f"**{row['Category']}**")
            col_b.progress(row['Progress'], text=f"{row['Actual']:,} / {row['Budget']:,} ({row['Status']})")

    else:
        st.info("`config/budget.json` が設定されていません。")

with tab3:
    st.header("Recent Transactions")
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT transaction_date, category, genre, amount, comment, source FROM transactions ORDER BY transaction_date DESC LIMIT 100"
    df_tx = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df_tx.empty:
        st.dataframe(df_tx, use_container_width=True)
    else:
        st.info("取引データがありません。")

with tab4:
    st.header("AI Analysis History")
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT created_at, timeframe, score, summary, report_path FROM analysis_history ORDER BY created_at DESC"
    df_hist = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df_hist.empty:
        for index, row in df_hist.iterrows():
            with st.expander(f"{row['created_at']} - {row['timeframe']} (Score: {row['score']})"):
                st.write(f"**Summary:** {row['summary']}")
                if row['report_path'] and os.path.exists(row['report_path']):
                    with open(row['report_path'], "r", encoding="utf-8") as f:
                        st.markdown(f.read())
                else:
                    st.caption("詳細レポートファイルが見つかりません。")
    else:
        st.info("AI分析履歴がありません。")

st.sidebar.markdown("---")
st.sidebar.caption("Kakeibo AI Review System v1.1")
