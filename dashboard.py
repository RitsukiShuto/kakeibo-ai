import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
from src.db.database import Database
from dotenv import load_dotenv

# ページ設定 (サイドバーなし、ワイドモード)
st.set_page_config(page_title="Kakeibo AI Dashboard", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

# 環境変数の読み込み
load_dotenv("local/.env")

# データベース接続
DB_PATH = "local/kakeibo.db"
db = Database(db_path=DB_PATH)

def load_budget():
    budget_path = "local/config/budget.json"
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def render_dashboard_content(timeframe):
    col_left, col_right = st.columns(2)

    # --- 左側カラム (TL: 予実, BL: 資産) ---
    with col_left:
        # 1. 予実管理 (Top-Left)
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

            # カテゴリ別進捗
            st.write("**Category Progress**")
            cols = st.columns(2)
            for i, (cat, b_amt) in enumerate(budget_categories.items()):
                actual_row = df_actual[df_actual['category'] == cat]
                a_amt = int(actual_row['actual'].iloc[0]) if not actual_row.empty else 0
                progress = min(a_amt / b_amt, 1.0) if b_amt > 0 else 0
                
                with cols[i % 2]:
                    st.write(f"{cat}: {a_amt:,} / {b_amt:,}")
                    st.progress(progress)
        else:
            st.info("`local/config/budget.json` が設定されていません。")

        st.divider()

        # 2. 資産推移 (Bottom-Left)
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

    # --- 右側カラム (TR: レビュー, BR: 明細) ---
    with col_right:
        # 3. AIレビュー (Top-Right)
        st.subheader("🤖 AI Analysis Report")
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT created_at, timeframe, score, summary, report_path FROM analysis_history WHERE timeframe = '{timeframe}' ORDER BY created_at DESC"
        df_hist = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_hist.empty:
            latest = df_hist.iloc[0]
            # 最新のレビューを全文表示（省略なし）
            st.success(f"### Score: {latest['score']} ({latest['created_at']})")
            st.info(f"**Summary**\n\n{latest['summary']}")
            
            if latest['report_path'] and os.path.exists(latest['report_path']):
                with open(latest['report_path'], "r", encoding="utf-8") as f:
                    st.markdown("---")
                    st.markdown(f.read())
            
            # 過去の履歴はアコーディオンに収納
            if len(df_hist) > 1:
                st.write("**Previous Reviews History**")
                for index, row in df_hist.iloc[1:5].iterrows():
                    with st.expander(f"{row['created_at']} (Score: {row['score']})"):
                        st.write(row['summary'])
        else:
            st.info(f"{timeframe} の分析履歴がありません。")

        st.divider()

        # 4. 立替・精算管理 (AI Expense Splitter)
        st.subheader("🤝 AI Expense Splitter")
        
        # 4a. 未精算リスト
        conn = sqlite3.connect(DB_PATH)
        query_pending = """
        SELECT transaction_date, category, amount, self_amount, (amount - IFNULL(self_amount, 0)) as pending_amount, comment, transaction_id
        FROM transactions 
        WHERE is_reimbursement = 1 AND reimbursement_status != 'completed'
        ORDER BY transaction_date DESC
        """
        df_pending = pd.read_sql_query(query_pending, conn)
        
        if not df_pending.empty:
            st.warning(f"精算待ち項目: {len(df_pending)} 件 (合計: {df_pending['pending_amount'].sum():,}円)")
            st.dataframe(df_pending.drop(columns=['transaction_id']), use_container_width=True)
            
            # 精算完了ボタン（簡易版）
            with st.expander("精算を完了する"):
                target_tx = st.selectbox("精算完了にする明細を選択", df_pending['transaction_id'].tolist(), 
                                         format_func=lambda x: f"{df_pending[df_pending['transaction_id']==x]['transaction_date'].iloc[0]} - {df_pending[df_pending['transaction_id']==x]['comment'].iloc[0]} ({df_pending[df_pending['transaction_id']==x]['pending_amount'].iloc[0]}円)")
                if st.button("精算完了としてマーク"):
                    cursor = conn.cursor()
                    cursor.execute("UPDATE transactions SET reimbursement_status = 'completed' WHERE transaction_id = ?", (target_tx,))
                    conn.commit()
                    st.success("精算を完了しました！")
                    st.rerun()
        else:
            st.success("未精算の項目はありません。ととのってる〜！💅")
        
        st.write("---")
        
        # 4b. 新しく立替を設定
        st.write("**Recent Transactions to Split**")
        query_recent = "SELECT transaction_id, transaction_date, category, amount, comment FROM transactions WHERE mode='payment' AND is_reimbursement=0 ORDER BY transaction_date DESC LIMIT 10"
        df_recent = pd.read_sql_query(query_recent, conn)
        
        if not df_recent.empty:
            selected_tx_id = st.selectbox("立替設定する明細を選択", df_recent['transaction_id'].tolist(),
                                          format_func=lambda x: f"{df_recent[df_recent['transaction_id']==x]['transaction_date'].iloc[0]} - {df_recent[df_recent['transaction_id']==x]['comment'].iloc[0]} ({df_recent[df_recent['transaction_id']==x]['amount'].iloc[0]}円)")
            
            target_row = df_recent[df_recent['transaction_id'] == selected_tx_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                self_amt = st.number_input("自分の負担額 (円)", min_value=0, max_value=int(target_row['amount']), value=int(target_row['amount']//2))
            with col2:
                st.write(f"立替額: {target_row['amount'] - self_amt:,} 円")
                if st.button("立替として設定"):
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE transactions 
                        SET is_reimbursement = 1, self_amount = ?, reimbursement_status = 'pending' 
                        WHERE transaction_id = ?
                    """, (self_amt, selected_tx_id))
                    conn.commit()
                    st.success("立替設定を保存しました！")
                    st.rerun()
        
        conn.close()

        st.divider()

        # 5. 最近の明細 (Bottom-Right)
        st.subheader("📝 Recent Transactions")
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT transaction_date, category, amount, 
               CASE WHEN is_reimbursement=1 THEN self_amount ELSE amount END as 'Net Amount',
               comment, is_reimbursement as 'Split?'
        FROM transactions 
        ORDER BY transaction_date DESC LIMIT 50
        """
        df_tx = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_tx.empty:
            st.dataframe(df_tx, use_container_width=True, height=400)
        else:
            st.caption("取引データがありません。")

st.title("📊 Kakeibo AI Integrated Dashboard")

# トップタブによる集計期間の切り替え
timeframe_list = ["weekly", "monthly", "quarterly", "yearly"]
tabs = st.tabs([tf.capitalize() for tf in timeframe_list])

for i, tab in enumerate(tabs):
    with tab:
        render_dashboard_content(timeframe_list[i])

# 下部にリフレッシュボタン
if st.button("🔄 Refresh Data"):
    st.rerun()
