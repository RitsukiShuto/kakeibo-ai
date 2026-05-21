import os
import json
import re
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from src.models import Transaction, Asset, AIResponse
from .providers.factory import LLMFactory

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

class KakeiboAnalyzer:
    def __init__(self):
        self.provider = LLMFactory.create_provider()
        self.model_name = self.provider.get_model_name()

    def _get_active_persona(self):
        # 設定ファイルから現在のキャラクターを取得
        settings_path = "local/config/settings.json"
        persona = 'gal' # デフォルト
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    persona = settings.get("ai", {}).get("active_persona", persona)
            except Exception as e:
                print(f"Warning: Failed to load settings.json, using default persona: {e}")
        return persona

    def analyze_kakeibo(self, data: List[Transaction], assets_summary: List[dict], timeframe: str, profile: dict, budget: dict = None, previous_summary: Optional[str] = None, actual_monthly_income: int = 0, comparison_data: dict = None, pending_reimbursements: List[Transaction] = None) -> Optional[AIResponse]:
        # 1. 各種プロンプトファイルの読み込み
        active_persona = self._get_active_persona()
        persona_path = f"prompts/personas/{active_persona}.md"
        if not os.path.exists(persona_path):
            persona_path = "prompts/personas/default.md"
            
        persona_settings = self._load_prompt_file(persona_path)
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

    def parse_reimbursement_text(self, text: str, total_amount: int) -> Optional[dict]:
        """
        立替に関する自然言語入力を解析し、自己負担額を算出する
        """
        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。ユーザーが入力した立替や割り勘に関する説明を解析し、"
            "「ユーザー自身の自己負担額」を算出してください。\n"
            "入力には、総額、人数、あるいは特定の金額が含まれる場合があります。\n"
            "返却は以下のJSON形式のみで行ってください。\n"
            "{\"self_amount\": 整数, \"reason\": \"算出した理由の短い説明\"}"
        )

        user_input = f"総額: {total_amount}円\n説明: {text}"

        try:
            raw_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_input,
                response_mime_type="application/json",
                temperature=0.1
            )
            result = json.loads(raw_text.strip())
            return result
        except Exception as e:
            print(f"Error parsing reimbursement text: {e}")
            return None

    def detect_potential_reimbursements(self, transactions: List[Transaction]) -> List[dict]:
        """
        最近の明細から立替の可能性がある項目をAIで推測する
        """
        if not transactions:
            return []

        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。支払い明細のリストを見て、"
            "「これは実は立替や割り勘なのではないか？」と思われる項目をピックアップしてください。\n"
            "高額な外食、複数人での利用が推測される場所、普段の支出パターンと異なるものなどが候補になります。\n"
            "返却は以下のJSON形式のみで行ってください。\n"
            "{\"suggestions\": [{\"transaction_id\": \"ID\", \"reason\": \"推測理由\", \"confidence\": 0.0-1.0}]}"
        )

        tx_list_text = "\n".join([
            f"- ID: {t.transaction_id}, 日付: {t.transaction_date}, カテゴリ: {t.category}, 金額: {t.amount}円, 内容: {t.comment}"
            for t in transactions
        ])

        try:
            raw_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=f"対象明細:\n{tx_list_text}",
                response_mime_type="application/json",
                temperature=0.1
            )
            result = json.loads(raw_text.strip())
            return result.get("suggestions", [])
        except Exception as e:
            print(f"Error detecting reimbursements: {e}")
            return []

    def suggest_category_mappings(self, unmapped_items: List[dict], target_categories: List[str]) -> List[dict]:
        """
        未マッピングの項目に対して、予算カテゴリへのマッピングを提案する
        """
        if not unmapped_items or not target_categories:
            return []

        system_prompt = (
            "あなたは優秀な家計簿アシスタントです。金融サービスから取得した「元のカテゴリ・中項目」を、"
            "ユーザーが設定した「予算カテゴリ」のどれに分類すべきか提案してください。\n"
            "可能な限り正確に分類し、判断がつかない場合は最も近いものを選んでください。\n"
            "返却は以下のJSON形式のみで行ってください。コードブロックは含めないでください。\n"
            "{\"suggestions\": [{\"raw_category\": \"元の大項目\", \"raw_genre\": \"元の中項目\", \"suggested_category\": \"予算カテゴリ名\", \"suggested_genre\": \"提案する中項目名\", \"reason\": \"理由\"}]}"
        )

        user_input = {
            "unmapped_items": unmapped_items,
            "target_categories": target_categories
        }

        try:
            raw_text = self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=f"対象データ:\n{json.dumps(user_input, ensure_ascii=False)}",
                response_mime_type="application/json",
                temperature=0.1
            )
            result = json.loads(raw_text.strip())
            return result.get("suggestions", [])
        except Exception as e:
            print(f"Error suggesting category mappings: {e}")
            return []

    def analyze_life_plan(self, trajectory: List[dict], profile: dict, budget: dict) -> str:
        """
        ライフプランシミュレーションの結果を元にAIアドバイスを生成する
        """
        active_persona = self._get_active_persona()
        persona_path = f"prompts/personas/{active_persona}.md"
        if not os.path.exists(persona_path):
            persona_path = "prompts/personas/default.md"
            
        persona_settings = self._load_prompt_file(persona_path)
        
        user_info = profile.get("user", {})
        life_plan = user_info.get("life_plan", {})
        
        system_prompt = (
            f"{persona_settings}\n\n"
            "あなたは優秀なファイナンシャルプランナー兼ライフプランアドバイザーです。"
            "提供された資産シミュレーションの結果を見て、ユーザーの将来に向けたアドバイスを行ってください。\n"
            "特に以下の点に注目してください：\n"
            "1. 現在の貯蓄・投資ペースで目標（FIREや老後資金）を達成できるか\n"
            "2. 改善が必要な場合の具体的なアクション（節約や投資割合の変更など）\n"
            "3. ライフイベント（住宅購入など）が将来の資産に与える影響\n"
        )
        
        # 重要な年齢のデータを抽出
        key_ages = [life_plan.get("retirement_age"), 80, 100]
        summary_trajectory = [t for t in trajectory if t["age"] in key_ages or t["age"] == trajectory[0]["age"]]
        
        user_input = {
            "profile": life_plan,
            "monthly_savings_goal": budget.get("monthly", {}).get("savings_goal", 0) + budget.get("monthly", {}).get("investment_goal", 0),
            "simulation_summary": summary_trajectory
        }

        try:
            return self.provider.generate_content(
                system_prompt=system_prompt,
                user_prompt=f"シミュレーションデータ:\n{json.dumps(user_input, ensure_ascii=False)}",
                temperature=0.7
            )
        except Exception as e:
            print(f"Life plan analysis error: {e}")
            return "シミュレーション結果の分析中にエラーが発生したよ。データを見直してみてね！"

    def chat(self, message: str, history: List[dict] = None, profile: dict = None, budget: dict = None, assets_summary: List[dict] = None, recent_transactions: List[Transaction] = None, model_override: str = None) -> str:
        """
        家計に関するインタラクティブなチャット回答を生成する
        """
        active_persona = self._get_active_persona()
        persona_path = f"prompts/personas/{active_persona}.md"
        if not os.path.exists(persona_path):
            persona_path = "prompts/personas/default.md"
            
        persona_settings = self._load_prompt_file(persona_path)
        
        system_prompt = (
            f"{persona_settings}\n\n"
            "あなたは優秀な家計簿アシスタントです。ユーザーからの質問に対して、"
            "現在の家計状況を考慮した具体的で親しみやすいアドバイスを提供してください。\n"
        )
        
        if assets_summary:
            total = sum(a['amount'] for a in assets_summary)
            system_prompt += f"\n現在の総資産: {total:,}円\n"
            system_prompt += "資産内訳:\n" + "\n".join([f"- {a['category']}: {a['amount']:,}円" for a in assets_summary])
            
        if recent_transactions:
            system_prompt += "\n\n最近の支出明細（直近10件）:\n"
            for t in recent_transactions[:10]:
                system_prompt += f"- {t.transaction_date}: {t.category}({t.genre}) {t.amount}円 {t.comment}\n"

        original_model = None
        if model_override:
            original_model = self.provider.model_name
            self.provider.model_name = model_override

        try:
            result = self.provider.chat(
                system_prompt=system_prompt,
                history=history or [],
                message=message,
                temperature=0.7
            )
            if original_model:
                self.provider.model_name = original_model
            return result
        except Exception as e:
            if original_model:
                self.provider.model_name = original_model
            print(f"Chat error: {e}")
            return "ごめん、ちょっと調子が悪いみたい。後でもう一度話しかけてね！"

    def _load_prompt_file(self, file_path: str) -> str:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _calculate_statistics(self, data: List[Transaction], budget: dict = None) -> dict:
        """
        明細データから統計情報を算出する
        """
        stats = {
            "total_income": 0,
            "total_expense": 0,
            "category_totals": {},
            "budget_usage": {},
            "high_spending": []
        }
        
        # カテゴリ別集計
        for t in data:
            if t.mode == "income":
                stats["total_income"] += t.amount
            elif t.mode == "payment":
                amount = t.self_amount if t.is_reimbursement and t.self_amount is not None else t.amount
                stats["total_expense"] += amount
                
                cat = t.category
                stats["category_totals"][cat] = stats["category_totals"].get(cat, 0) + amount
                
                # 高額支出（1万円以上）
                if amount >= 10000:
                    stats["high_spending"].append({
                        "date": t.transaction_date,
                        "category": t.category,
                        "amount": amount,
                        "comment": t.comment
                    })

        # 高額支出を金額順にソート
        stats["high_spending"].sort(key=lambda x: x["amount"], reverse=True)

        # 予算消化率
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
        
        # daily 専用の追加情報
        if timeframe == "daily":
            from datetime import datetime
            now = datetime.now()
            import calendar
            days_in_month = calendar.monthrange(now.year, now.month)[1]
            remaining_days = days_in_month - now.day
            
            # 固定費合計の計算
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
                text += "- 特筆すべき高額支出:\n"
                for h in stats["high_spending"][:5]: # 上位5件
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
            # 純資産の前月比
            if "prev_total_assets" in comparison_data:
                curr = sum(a['amount'] for a in assets_summary)
                prev = comparison_data["prev_total_assets"]
                diff = curr - prev
                ratio = (diff / prev * 100) if prev != 0 else 0
                text += f"- 純資産の前月比: {diff:+,}円 ({ratio:+.1f}%)\n"
            
            # 収支の改善度合い
            if "prev_balance" in comparison_data:
                curr_income = actual_monthly_income
                # 立替を考慮した支出計算
                curr_expense = stats['total_expense'] if stats else sum(
                    (t.self_amount if t.is_reimbursement and t.self_amount is not None else t.amount)
                    for t in data if t.mode == 'payment'
                )
                curr_bal = curr_income - curr_expense
                
                prev_bal = comparison_data["prev_balance"]
                bal_diff = curr_bal - prev_bal
                
                # 改善率の計算 (分母が0または負の場合の考慮が必要だが、簡易的に)
                if prev_bal != 0:
                    bal_ratio = (bal_diff / abs(prev_bal) * 100)
                else:
                    bal_ratio = 0
                
                text += f"- 収支の改善度 (前期間比): {bal_diff:+,}円 ({bal_ratio:+.1f}%)\n"
            text += "\n"

        text += f"#### {4 if stats else 3}. 今回追加された差分明細\n"
        if not data:
            text += "なし\n"
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

class GeminiAnalyzer(KakeiboAnalyzer):
    """
    Backward compatibility class name.
    """
    pass
