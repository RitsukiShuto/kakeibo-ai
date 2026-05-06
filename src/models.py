from datetime import date as date_type
from typing import Optional, List
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    """
    家計簿の明細データモデル
    """
    transaction_id: Optional[str] = Field(None, description="明細の一意識別子（MFやZaimのIDなど）")
    transaction_date: date_type = Field(..., description="決済日")
    category: str = Field(..., description="大項目（食費、住居費など）")
    genre: str = Field("", description="中項目（外食、家賃など）")
    amount: int = Field(..., description="金額")
    comment: str = Field("", description="備考・内容")
    source: str = Field(..., description="データ元")
    mode: str = Field(..., description="区分（payment, income, transfer）")

class Asset(BaseModel):
    """
    資産状況データモデル
    """
    acquired_date: date_type = Field(..., description="取得日")
    asset_type: str = Field(..., description="資産の種類")
    amount: int = Field(..., description="金額")
    source: str = Field(..., description="データ元")
    institution: Optional[str] = Field(None, description="金融機関名")

class AIAction(BaseModel):
    command: str = Field(..., description="コマンド名")
    description: str = Field(..., description="内容")

class AssetBreakdown(BaseModel):
    category: str = Field(..., description="資産カテゴリ（例：預金・現金、投資信託、株式など）")
    amount: int = Field(..., description="そのカテゴリの合計金額")

class BudgetStatus(BaseModel):
    category: str = Field(..., description="カテゴリ名")
    budget: int = Field(..., description="予算額")
    actual: int = Field(..., description="実績額")
    status: str = Field(..., description="状態（OK, 警告, 超過など）")

class AIResponse(BaseModel):
    slack_report: str = Field(..., description="Slack用詳細レポート")
    obsidian_report: str = Field(..., description="Obsidian用レポート")
    actions: List[AIAction] = Field(..., description="アクションリスト")
    asset_breakdown: List[AssetBreakdown] = Field(..., description="資産のカテゴリ別内訳")
    budget_status: List[BudgetStatus] = Field(default_factory=list, description="予算の達成状況")
    totonoi_score: int = Field(..., description="ととのい指数")
    savings_potential: int = Field(..., description="節約可能額")
