from typing import List, Dict
import math

class LifePlanCalculator:
    def __init__(self, 
                 current_assets: int,
                 monthly_savings: int,
                 current_age: int,
                 retirement_age: int,
                 annual_return_rate: float,
                 annual_inflation_rate: float,
                 monthly_expenses_post_retirement: int,
                 events: List[Dict] = None):
        self.current_assets = current_assets
        self.monthly_savings = monthly_savings
        self.current_age = current_age
        self.retirement_age = retirement_age
        self.annual_return_rate = annual_return_rate / 100.0
        self.annual_inflation_rate = annual_inflation_rate / 100.0
        self.monthly_expenses_post_retirement = monthly_expenses_post_retirement
        self.events = events or []

    def simulate(self, end_age: int = 100) -> List[Dict]:
        trajectory = []
        assets = self.current_assets
        
        # 月次計算
        for age in range(self.current_age, end_age + 1):
            # イベントの適用 (年初に適用と仮定)
            event_total = sum(e['amount'] for e in self.events if e['age'] == age)
            assets -= event_total
            
            # 年間の推移を記録
            trajectory.append({
                "age": age,
                "assets": int(assets),
                "is_retired": age >= self.retirement_age
            })
            
            # 月次での更新 (利息、入金/出金、インフレ)
            # 月利 = (1 + 年利)^(1/12) - 1
            monthly_return = (1 + self.annual_return_rate)**(1/12) - 1
            # 月次インフレ = (1 + 年次インフレ)^(1/12) - 1
            monthly_inflation = (1 + self.annual_inflation_rate)**(1/12) - 1
            
            for _ in range(12):
                if age < self.retirement_age:
                    # 働いている期間: 貯蓄
                    assets += self.monthly_savings
                else:
                    # 引退後: 取り崩し (インフレ考慮)
                    # 物価上昇に伴い、必要生活費も上がるとする
                    inflation_factor = (1 + monthly_inflation)**((age - self.retirement_age)*12 + _)
                    current_expenses = self.monthly_expenses_post_retirement * inflation_factor
                    assets -= current_expenses
                
                # 運用益の加算
                assets *= (1 + monthly_return)
            
            if assets < -100000000: # 破産しすぎたら停止
                break
                
        return trajectory
