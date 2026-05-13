import os
from datetime import datetime, date, timedelta
from typing import List
from pyzaim import ZaimAPI
from dotenv import load_dotenv
from src.models import Transaction, Asset
from src.fetcher.base_fetcher import BaseFetcher
from src.utils.category_mapper import CategoryMapper

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

class ZaimFetcher(BaseFetcher):
    def __init__(self):
        consumer_id = os.getenv("ZAIM_CONSUMER_ID")
        consumer_secret = os.getenv("ZAIM_CONSUMER_SECRET")
        access_token = os.getenv("ZAIM_ACCESS_TOKEN")
        access_token_secret = os.getenv("ZAIM_ACCESS_TOKEN_SECRET")

        if not all([consumer_id, consumer_secret, access_token, access_token_secret]):
            raise ValueError("Zaim API keys are missing.")

        self.api = ZaimAPI(consumer_id, consumer_secret, access_token, access_token_secret, oauth_verifier=None)
        self.categories = self.api.category()
        self.genres = self.api.genre()
        self.mapper = CategoryMapper()

    def fetch_transactions(self, days: int = 30) -> List[Transaction]:
        today = date.today()
        start_date = today - timedelta(days=days)
        
        raw_data = self.api.data(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=today.strftime("%Y-%m-%d")
        )
        
        transactions = []
        for item in raw_data:
            raw_category = self._get_category_name(item["category_id"])
            raw_genre = self._get_genre_name(item["genre_id"])
            
            # カテゴリマッピングの適用
            mapped_category, mapped_genre = self.mapper.apply_mapping(raw_category, raw_genre)

            transactions.append(Transaction(
                transaction_id=str(item["id"]),
                transaction_date=date.fromisoformat(item["date"]),
                category=mapped_category,
                genre=mapped_genre,
                amount=item["amount"],
                comment=item["comment"] or "",
                source="Zaim",
                mode=item["mode"]
            ))
        return transactions

    def fetch_assets(self) -> List[Asset]:
        accounts = self.api.account()
        assets = []
        today = date.today()
        
        for acc in accounts:
            if acc["active"] != -1:
                assets.append(Asset(
                    acquired_date=today,
                    asset_type="Unknown",
                    amount=acc["balance"],
                    source="Zaim",
                    institution=acc["name"]
                ))
        return assets

    def _get_category_name(self, category_id):
        for cat in self.categories:
            if str(cat["id"]) == str(category_id):
                return cat["name"]
        return "Unknown"

    def _get_genre_name(self, genre_id):
        for gen in self.genres:
            if str(gen["id"]) == str(genre_id):
                return gen["name"]
        return "Unknown"
