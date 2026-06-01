import json
import os
from typing import List
from .base import BaseAnalyzer

class LifePlanAnalyzer(BaseAnalyzer):
    def analyze_life_plan(self, trajectory: List[dict], profile: dict, budget: dict) -> str:
        persona_settings = self._get_persona_settings()
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
