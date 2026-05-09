import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
from src.db.database import Database
from dotenv import load_dotenv

# ページ設定 (サイドバーあり、ワイドモード)
st.set_page_config(page_title="Kakeibo AI Dashboard", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

# --- カスタムCSS (プロトタイプのダークテーマを反映) ---
st.markdown("""
<style>
    /* 全体の背景と文字色 */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    /* サイドバー */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    /* カード風のコンテナ */
    div.stMetric {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.5);
    }
    /* サブヘッダーの装飾 */
    .stMarkdown h2, .stMarkdown h3 {
        color: #3b82f6;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }
    /* ボタンのスタイル */
    .stButton>button {
        border-radius: 8px;
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 環境変数の読み込み
load_dotenv("local/.env")

# データベース接続
DB_PATH = os.getenv("KAKEIBO_DB_PATH", "local/kakeibo.db")
db = Database(db_path=DB_PATH)

def load_budget():
    budget_path = "local/config/budget.json"
    if os.path.exists(budget_path):
        with open(budget_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 互換性維持: 旧形式（categoriesが直接フラット）の場合は新形式にラップする
            if "budget" not in data.get("monthly", {}):
                old_categories = data.get("monthly", {}).get("categories", {})
                data["monthly"]["budget"] = {"variable": {"その他": old_categories}}
            return data
    return None

def get_budget_category_totals(budget):
    """
    階層型予算から中項目ごとの合計金額を計算してフラットな辞書で返す
    """
    totals = {}
    if not budget:
        return totals
    
    monthly_budget = budget.get("monthly", {}).get("budget", {})
    for section in ["fixed", "variable"]:
        section_data = monthly_budget.get(section, {})
        for category, subcategories in section_data.items():
            if isinstance(subcategories, dict):
                totals[category] = sum(subcategories.values())
            else:
                totals[category] = subcategories
    return totals

def render_dashboard_content(timeframe):
    budget = load_budget()
    budget_categories = get_budget_category_totals(budget)
    
    # --- 1. KPI カード (最上部) ---
    current_month = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB_PATH)
    query_total = f"SELECT SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as total FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment'"
    actual_total = pd.read_sql_query(query_total, conn)['total'].iloc[0] or 0
    
    query_assets = "SELECT SUM(amount) as total FROM assets WHERE acquired_date = (SELECT MAX(acquired_date) FROM assets)"
    total_assets = pd.read_sql_query(query_assets, conn)['total'].iloc[0] or 0
    conn.close()

    total_budget_amt = sum(budget_categories.values()) if budget_categories else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("予算 (Budget)", f"{total_budget_amt:,}円")
    kpi2.metric("実支出 (Actual)", f"{int(actual_total):,}円", delta=f"{total_budget_amt - actual_total:,}円", delta_color="inverse")
    kpi3.metric("残額 (Remaining)", f"{max(0, total_budget_amt - int(actual_total)):,}円")
    kpi4.metric("総資産 (Total Assets)", f"{int(total_assets):,}円")

    st.divider()

    col_left, col_right = st.columns(2)

    # --- 左側カラム (予実 & 資産) ---
    with col_left:
        st.subheader("⚖️ 予実管理 (カテゴリ別)")
        if budget_categories:
            conn = sqlite3.connect(DB_PATH)
            query = f"SELECT category, SUM(CASE WHEN is_reimbursement=1 AND self_amount IS NOT NULL THEN self_amount ELSE amount END) as actual FROM transactions WHERE transaction_date LIKE '{current_month}%' AND mode='payment' GROUP BY category"
            df_actual = pd.read_sql_query(query, conn)
            conn.close()

            for cat, b_amt in budget_categories.items():
                actual_row = df_actual[df_actual['category'] == cat]
                a_amt = int(actual_row['actual'].iloc[0]) if not actual_row.empty else 0
                progress = min(a_amt / b_amt, 1.0) if b_amt > 0 else 0
                st.write(f"**{cat}**: {a_amt:,} / {b_amt:,}")
                st.progress(progress)
        else:
            st.info("予算が設定されていません。")

        st.subheader("📈 資産推移")
        conn = sqlite3.connect(DB_PATH)
        df_assets = pd.read_sql_query("SELECT acquired_date, asset_type, SUM(amount) as total_amount FROM assets GROUP BY acquired_date, asset_type ORDER BY acquired_date ASC", conn)
        conn.close()
        if not df_assets.empty:
            df_assets['acquired_date'] = pd.to_datetime(df_assets['acquired_date'])
            pivot_df = df_assets.pivot(index='acquired_date', columns='asset_type', values='total_amount').fillna(0)
            st.area_chart(pivot_df, height=300)

    # --- 右側カラム (AIレビュー & 最近の明細) ---
    with col_right:
        st.subheader("🤖 AI 分析レポート")
        conn = sqlite3.connect(DB_PATH)
        df_hist = pd.read_sql_query(f"SELECT created_at, score, summary, report_path FROM analysis_history WHERE timeframe = '{timeframe}' ORDER BY created_at DESC", conn)
        conn.close()
        if not df_hist.empty:
            latest = df_hist.iloc[0]
            st.success(f"### Score: {latest['score']} ({latest['created_at']})")
            st.info(latest['summary'])
            with st.expander("レポート詳細を表示"):
                if latest['report_path'] and os.path.exists(latest['report_path']):
                    with open(latest['report_path'], "r", encoding="utf-8") as f:
                        st.markdown(f.read())
        
        st.subheader("📝 最近の明細")
        conn = sqlite3.connect(DB_PATH)
        df_tx = pd.read_sql_query("SELECT transaction_date as '日付', category as 'カテゴリ', amount as '金額', comment as '内容' FROM transactions ORDER BY transaction_date DESC LIMIT 10", conn)
        conn.close()
        st.table(df_tx)

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
            st.dataframe(df_pending.drop(columns=['transaction_id']), width='stretch')
            
            # 精算完了ボタン（簡易版）
            with st.expander("精算を完了する"):
                target_tx = st.selectbox("精算完了にする明細を選択", df_pending['transaction_id'].tolist(), 
                                         key=f"complete_{timeframe}",
                                         format_func=lambda x: f"{df_pending[df_pending['transaction_id']==x]['transaction_date'].iloc[0]} - {df_pending[df_pending['transaction_id']==x]['comment'].iloc[0]} ({df_pending[df_pending['transaction_id']==x]['pending_amount'].iloc[0]}円)")
                if st.button("精算完了としてマーク", key=f"btn_complete_{timeframe}"):
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
                                          key=f"split_select_{timeframe}",
                                          format_func=lambda x: f"{df_recent[df_recent['transaction_id']==x]['transaction_date'].iloc[0]} - {df_recent[df_recent['transaction_id']==x]['comment'].iloc[0]} ({df_recent[df_recent['transaction_id']==x]['amount'].iloc[0]}円)")
            
            target_row = df_recent[df_recent['transaction_id'] == selected_tx_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                # AI解析の追加
                ai_input = st.text_input("AIで計算 (例: 4人で割り勘, 自分は5000円など)", key=f"ai_input_{timeframe}")
                if ai_input:
                    from src.analyzer.gemini_analyzer import GeminiAnalyzer
                    analyzer = GeminiAnalyzer()
                    with st.spinner("AIが計算中..."):
                        ai_result = analyzer.parse_reimbursement_text(ai_input, target_row['amount'])
                        if ai_result:
                            st.info(f"AI提案: {ai_result['self_amount']:,}円 ({ai_result['reason']})")
                            st.session_state[f"self_amt_val_{timeframe}"] = ai_result['self_amount']
                
                # 初期値の管理
                default_val = st.session_state.get(f"self_amt_val_{timeframe}", int(target_row['amount']//2))
                self_amt = st.number_input("自分の負担額 (円)", min_value=0, max_value=int(target_row['amount']), 
                                          value=default_val,
                                          key=f"self_amt_{timeframe}")
            with col2:
                st.write(f"立替額: {target_row['amount'] - self_amt:,} 円")
                if st.button("立替として設定", key=f"btn_split_{timeframe}"):
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE transactions 
                        SET is_reimbursement = 1, self_amount = ?, reimbursement_status = 'pending' 
                        WHERE transaction_id = ?
                    """, (self_amt, selected_tx_id))
                    conn.commit()
                    if f"self_amt_val_{timeframe}" in st.session_state:
                        del st.session_state[f"self_amt_val_{timeframe}"]
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

def render_transactions_page():
    st.subheader("📝 明細一覧・編集")
    
    # フィルタと検索
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("明細を検索", placeholder="摘要やカテゴリで検索...")
    
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM transactions ORDER BY transaction_date DESC"
    df_tx = pd.read_sql_query(query, conn)
    conn.close()

    if search_query:
        df_tx = df_tx[df_tx['comment'].str.contains(search_query, na=False) | df_tx['category'].str.contains(search_query, na=False)]

    if not df_tx.empty:
        # 編集可能なデータフレームを表示（簡易的な実装として、選択した行を編集するUIにする）
        st.write(f"表示件数: {len(df_tx)} 件")
        
        # 簡易的なテーブル表示と個別編集フォーム
        for index, row in df_tx.head(20).iterrows():
            with st.expander(f"{row['transaction_date']} | {row['category']} | {row['amount']:,}円 | {row['comment'] or ''}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_cat = st.text_input("カテゴリ", value=row['category'], key=f"cat_{row['transaction_id']}")
                    new_comment = st.text_input("摘要", value=row['comment'] or "", key=f"comm_{row['transaction_id']}")
                with col2:
                    is_reimb = st.checkbox("立替設定", value=bool(row['is_reimbursement']), key=f"reimb_{row['transaction_id']}")
                    if is_reimb:
                        self_amt = st.number_input("自己負担額", value=row['self_amount'] or row['amount']//2, key=f"self_{row['transaction_id']}")
                
                if st.button("更新を保存", key=f"save_{row['transaction_id']}"):
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE transactions 
                        SET category = ?, comment = ?, is_reimbursement = ?, self_amount = ?
                        WHERE transaction_id = ?
                    """, (new_cat, new_comment, 1 if is_reimb else 0, self_amt if is_reimb else None, row['transaction_id']))
                    conn.commit()
                    conn.close()
                    st.success("保存しました")
                    st.rerun()
    else:
        st.info("明細が見つかりません。")

def render_expense_splitter_page():
    st.subheader("🤝 AI 立替・精算管理")

    # --- これ立替？ (AI Detection) ---
    st.markdown("### 💡 これ立替？")
    if st.button("AIに立替の可能性を判定させる"):
        with st.spinner("AIが最近の明細を解析中..."):
            conn = sqlite3.connect(DB_PATH)
            # 直近の通常支出（立替設定されていないもの）を取得
            query = "SELECT * FROM transactions WHERE mode='payment' AND is_reimbursement=0 ORDER BY transaction_date DESC LIMIT 20"
            df_recent = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df_recent.empty:
                from src.analyzer.gemini_analyzer import GeminiAnalyzer
                analyzer = GeminiAnalyzer()
                # Transactionオブジェクトのリストに変換
                from src.models import Transaction
                from datetime import date
                transactions = [Transaction(
                    transaction_id=row['transaction_id'],
                    transaction_date=date.fromisoformat(row['transaction_date']),
                    category=row['category'],
                    amount=row['amount'],
                    comment=row['comment'],
                    source=row['source'],
                    mode=row['mode']
                ) for _, row in df_recent.iterrows()]
                
                suggestions = analyzer.detect_potential_reimbursements(transactions)
                st.session_state["reimb_suggestions"] = suggestions
            else:
                st.info("解析対象の明細がありません。")

    if "reimb_suggestions" in st.session_state and st.session_state["reimb_suggestions"]:
        suggestions = st.session_state["reimb_suggestions"]
        for sug in suggestions:
            # 該当する明細の詳細を取得
            conn = sqlite3.connect(DB_PATH)
            query = "SELECT * FROM transactions WHERE transaction_id = ?"
            tx_row = pd.read_sql_query(query, conn, params=(sug['transaction_id'],))
            conn.close()
            
            if not tx_row.empty:
                row = tx_row.iloc[0]
                with st.container():
                    st.warning(f"**{row['transaction_date']} | {row['comment']} | {row['amount']:,}円**")
                    st.write(f"🤖 **理由:** {sug['reason']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("立替にする", key=f"sug_yes_{row['transaction_id']}"):
                            # 簡易的に50%で設定
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("UPDATE transactions SET is_reimbursement=1, self_amount=?, reimbursement_status='pending' WHERE transaction_id=?", (row['amount']//2, row['transaction_id']))
                            conn.commit()
                            conn.close()
                            st.success("立替として登録しました")
                            st.rerun()
                    with col2:
                        if st.button("無視する", key=f"sug_no_{row['transaction_id']}"):
                            # 実際には「判定済み」フラグなどを立てるのが理想だが、ここではセッションから消すだけ
                            st.session_state["reimb_suggestions"] = [s for s in st.session_state["reimb_suggestions"] if s['transaction_id'] != row['transaction_id']]
                            st.rerun()
        st.divider()

    # --- 既存の精算待ちリストと新規登録 ---
    render_dashboard_content("monthly") # 暫定的に既存のロジックの一部を再利用、あるいは個別に実装

def render_settings_page():
    st.subheader("⚙️ システム設定")
    
    # 予算設定
    st.markdown("### ⚖️ 階層型予算設定")
    budget_data = load_budget()
    if budget_data:
        # JSONを直接編集できるテキストエリア（簡易実装）
        new_budget_json = st.text_area("budget.json (編集後、保存ボタンを押してください)", 
                                       value=json.dumps(budget_data, indent=2, ensure_ascii=False),
                                       height=400)
        if st.button("予算設定を保存"):
            try:
                parsed_json = json.loads(new_budget_json)
                with open("local/config/budget.json", "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                st.success("予算設定を更新しました")
                st.rerun()
            except Exception as e:
                st.error(f"JSONの形式が正しくありません: {e}")
    
    st.divider()
    
    # ペルソナ設定
    st.markdown("### 🤖 AI ペルソナ設定")
    profile_path = "local/config/profile.json"
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        
        new_profile_json = st.text_area("profile.json", 
                                        value=json.dumps(profile_data, indent=2, ensure_ascii=False),
                                        height=300)
        if st.button("プロフィール設定を保存"):
            try:
                parsed_json = json.loads(new_profile_json)
                with open(profile_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                st.success("プロフィール設定を更新しました")
                st.rerun()
            except Exception as e:
                st.error(f"JSONの形式が正しくありません: {e}")

def render_dashboard_page():
    # トップタブによる集計期間の切り替え
    timeframe_list = ["weekly", "monthly", "quarterly", "yearly"]
    tabs = st.tabs([tf.capitalize() for tf in timeframe_list])

    for i, tab in enumerate(tabs):
        with tab:
            render_dashboard_content(timeframe_list[i])

# --- サイドバーナビゲーション ---
with st.sidebar:
    st.title("💰 Kakeibo AI")
    page = st.radio("メニュー", ["ダッシュボード", "明細一覧", "AIレビュー", "立替・精算", "設定"])
    st.divider()
    if st.button("🔄 データを更新"):
        st.rerun()

if page == "ダッシュボード":
    render_dashboard_page()
elif page == "明細一覧":
    render_transactions_page()
elif page == "立替・精算":
    render_expense_splitter_page()
elif page == "設定":
    render_settings_page()
else:
    st.write(f"{page} ページは現在プロトタイプ開発中です。")
