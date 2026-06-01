import json
import re
from typing import List, Optional
from datetime import datetime
from src.models import Transaction, AIResponse
from .base import BaseAnalyzer

class ReviewAnalyzer(BaseAnalyzer):
    def analyze_kakeibo(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, profile: dict, budget: dict = None, previous_summary: Optional[str] = None, actual_monthly_income: int = 0, comparison_data: dict = None, pending_reimbursements: List[Transaction] = None) -> Optional[AIResponse]:
        # 1. 各種プロンプトファイルの読み込み
        persona_settings = self._get_persona_settings()
        system_prompt_template = self._load_prompt_file("prompts/system_prompt.md")
        timeframe_prompt = self._load_prompt_file(f"prompts/{timeframe}_prompt.md")
        output_structure = self._load_prompt_file("prompts/output_structure.md")
        
        # 2. システムプロンプトの構成
        user_info = profile.get("user", {})
        target = user_info.get("target", {})
        system_prompt = system_prompt_template.format(
            name=user_info.get('name', 'せんぱい'),
            occupation=user_info.get('occupation', '不明'),
            hobbies=', '.join(user_info.get('hobbies', [])),
            investment_policy=user_info.get('investment_policy', '未設定'),
            target_date=target.get('date', '未設定'),
            target_description=target.get('description', '目標なし')
        )
        full_system_prompt = f"{persona_settings}\n\n{system_prompt}"

        # 3. 統計データの事前計算
        stats = self._calculate_statistics(data, budget)

        # 4. ユーザープロンプト（分析対象データ）の構築
        user_input_text = self._create_user_input_text(
            data, assets_summary, timeframe, budget, 
            previous_summary, actual_monthly_income, 
            comparison_data, pending_reimbursements,
            stats=stats
        )

        user_prompt = (
            f"## 今回の分析の特別指示 ({timeframe})\n{timeframe_prompt}\n\n"
            f"## 分析対象データと統計情報\n{user_input_text}\n\n"
            f"{output_structure}"
        )

        print(f"AI analyzing {len(data)} transactions and {len(assets_summary)} asset categories...")
        
        try:
            raw_text = self.provider.generate_content(
                system_prompt=full_system_prompt,
                user_prompt=user_prompt,
                response_mime_type="application/json",
                temperature=0.7
            )
            
            # JSON部分の抽出（念のため）
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_candidate = raw_text[start_idx:end_idx+1]
            else:
                json_candidate = raw_text

            # 改行や余計な空白の削除（パースエラー対策）
            json_candidate = json_candidate.replace('\n', ' ').replace('\r', '')
            json_candidate = re.sub(r'\s+', ' ', json_candidate)

            result_json = json.loads(json_candidate)
            
            # 使用したモデル名を記録
            result_json["model_name"] = self.model_name
            
            ai_response = AIResponse(**result_json)
            return ai_response

        except Exception as e:
            print(f"AI Analysis error: {e}")
            return None

    def _calculate_statistics(self, data: List[Transaction], budget: dict = None) -> dict:
        stats = {
            "total_income": 0,
            "total_expense": 0,
            "category_totals": {},
            "category_counts": {},
            "budget_usage": {},
            "high_spending": []
        }
        
        for t in data:
            if t.mode == "income":
                stats["total_income"] += t.amount
            elif t.mode == "payment":
                amount = t.self_amount if t.is_reimbursement and t.self_amount is not None else t.amount
                stats["total_expense"] += amount
                
                cat = t.category
                stats["category_totals"][cat] = stats["category_totals"].get(cat, 0) + amount
                stats["category_counts"][cat] = stats["category_counts"].get(cat, 0) + 1
                
                if amount >= 10000:
                    stats["high_spending"].append({
                        "date": t.transaction_date,
                        "category": t.category,
                        "amount": amount,
                        "comment": t.comment
                    })

        stats["high_spending"].sort(key=lambda x: x["amount"], reverse=True)

        if budget and "monthly" in budget:
            monthly_categories = budget["monthly"].get("categories", {})
            for cat, b_amount in monthly_categories.items():
                actual = stats["category_totals"].get(cat, 0)
                usage_rate = (actual / b_amount * 100) if b_amount > 0 else 0
                stats["budget_usage"][cat] = {
                    "budget": b_amount,
                    "actual": actual,
                    "usage_rate": round(usage_rate, 1)
                }
                
        return stats

    def _create_user_input_text(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, budget: dict = None, previous_summary: Optional[str] = None, actual_monthly_income: int = 0, comparison_data: dict = None, pending_reimbursements: List[Transaction] = None, stats: dict = None) -> str:
        text = f"### 分析期間: {timeframe}\n\n"
        
        if timeframe == "daily":
            now = datetime.now()
            import calendar
            days_in_month = calendar.monthrange(now.year, now.month)[1]
            remaining_days = days_in_month - now.day
            
            fixed_expense_total = 0
            if budget and "monthly" in budget:
                fixed_categories = budget["monthly"].get("budget", {}).get("fixed", {})
                if fixed_categories:
                    def recursive_sum(d):
                        total = 0
                        for v in d.values():
                            if isinstance(v, dict):
                                total += recursive_sum(v)
                            elif isinstance(v, (int, float)):
                                total += v
                        return total
                    fixed_expense_total = recursive_sum(fixed_categories)
            
            text += "#### 📅 日次分析専用情報\n"
            text += f"- 集計基準日: {now.strftime('%Y年%m月%d日')}\n"
            text += f"- 今月の残り日数: {remaining_days}日（月末まで）\n"
            text += f"- 今月の固定費合計（日割り計算から除外する額）: {fixed_expense_total:,}円\n"
            text += f"- 今月の総日数: {days_in_month}日\n\n"
        
        if previous_summary:
            text += f"#### 0. 前回の分析サマリー\n{previous_summary}\n\n"

        if stats:
            text += "#### 1. 集計統計データ (Pythonによる事前計算)\n"
            text += f"- 合計収入: {stats['total_income']:,}円\n"
            text += f"- 合計支出: {stats['total_expense']:,}円\n"
            text += f"- 収支差分: {stats['total_income'] - stats['total_expense']:,}円\n"
            
            if stats["budget_usage"]:
                text += "- カテゴリ別予算消化状況:\n"
                for cat, s in stats["budget_usage"].items():
                    text += f"  - {cat}: 実績 {s['actual']:,}円 / 予算 {s['budget']:,}円 (消化率: {s['usage_rate']}%)\n"
            
            if stats["high_spending"]:
                text += "- 特筆すべき高額支出（上位10件）:\n"
                for h in stats["high_spending"][:10]:
                    text += f"  - {h['date']}: {h['category']} {h['amount']:,}円 ({h['comment']})\n"
            text += "\n"

        if budget:
            text += f"#### {2 if stats else 1}. 設定されている予算・収入状況 (月次)\n"
            monthly_budget = budget.get("monthly", {})
            budget_income = monthly_budget.get('income', 0)
            
            has_salary_arrived = actual_monthly_income >= (budget_income * 0.8)
            
            text += f"- 月間総収入予算: {budget_income:,}円\n"
            text += f"- 今月の現在までの実績収入: {actual_monthly_income:,}円\n"
            
            if has_salary_arrived:
                text += "👉 **【判定】今月の給料は受取済みです。分析には実績の収入額をベースに使用してください。**\n"
            else:
                text += f"👉 **【判定】今月の給料はまだ入っていないか、全額ではありません。分析には予算額（{budget_income:,}円）を暫定的な収入として参照してください。**\n"

            text += f"- 貯蓄目標: {monthly_budget.get('savings_goal', 0):,}円\n"
            text += f"- 投資目標: {monthly_budget.get('investment_goal', 0):,}円\n"
            text += "\n"

        if comparison_data:
            text += f"#### {3 if stats else 2}. 前期間との定量比較データ\n"
            if "prev_total_assets" in comparison_data:
                curr = sum(a['amount'] for a in assets_summary)
                prev = comparison_data["prev_total_assets"]
                diff = curr - prev
                ratio = (diff / prev * 100) if prev != 0 else 0
                text += f"- 純資産の前月比: {diff:+,}円 ({ratio:+.1f}%)\n"
            
            if "prev_balance" in comparison_data:
                curr_income = actual_monthly_income
                curr_expense = stats['total_expense'] if stats else sum(
                    (t.self_amount if t.is_reimbursement and t.self_amount is not None else t.amount)
                    for t in data if t.mode == 'payment'
                )
                curr_bal = curr_income - curr_expense
                prev_bal = comparison_data["prev_balance"]
                bal_diff = curr_bal - prev_bal
                bal_ratio = (bal_diff / abs(prev_bal) * 100) if prev_bal != 0 else 0
                text += f"- 収支の改善度 (前期間比): {bal_diff:+,}円 ({bal_ratio:+.1f}%)\n"
            text += "\n"

        text += f"#### {4 if stats else 3}. 今回追加された差分明細\n"
        if not data:
            text += "なし\n"
        elif timeframe in ["monthly", "quarterly", "yearly"] or len(data) > 30:
            text += f"※ 明細が多いため（{len(data)}件）、個別のリスト表示は省略しました。代わりにカテゴリ別の要約を以下に示します。\n"
            if stats:
                for cat, total in stats["category_totals"].items():
                    count = stats["category_counts"].get(cat, 0)
                    text += f"- {cat}: {count}件, 合計 {total:,}円\n"
            text += "\n上記の統計データおよび「特筆すべき高額支出」を重点的に分析してください。\n"
        else:
            for t in data:
                mode_ja = "支出" if t.mode == "payment" else "収入" if t.mode == "income" else "振替"
                amount_display = f"{t.amount}円"
                if t.is_reimbursement and t.self_amount is not None:
                    amount_display = f"{t.amount}円 (自己負担: {t.self_amount}円, 立替中)"
                text += f"- {t.transaction_date}: [{mode_ja}] {t.category}({t.genre}) {amount_display} {t.comment} [{t.source}]\n"

        if pending_reimbursements:
            text += f"\n#### {5 if stats else 4}. 未精算の立替金リスト (リマインド対象)\n"
            for t in pending_reimbursements:
                reimb_amt = t.amount - (t.self_amount or 0)
                text += f"- {t.transaction_date}: {t.category} {reimb_amt:,}円 (元金額: {t.amount:,}円) {t.comment}\n"

        text += f"\n#### {6 if stats else 5}. 現在の資産状況（カテゴリ別集計済み）\n"
        total_asset = 0
        for a in assets_summary:
            text += f"- {a['category']}: {a['amount']:,}円\n"
            total_asset += a['amount']
        text += f"**資産総額: {total_asset:,}円**\n"
        return text
