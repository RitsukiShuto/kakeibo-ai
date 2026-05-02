from abc import ABC, abstractmethod
from typing import List
from src.models import Transaction, Asset

class BaseFetcher(ABC):
    @abstractmethod
    def fetch_transactions(self) -> List[Transaction]:
        """
        入出金明細を取得する
        """
        pass

    @abstractmethod
    def fetch_assets(self) -> List[Asset]:
        """
        資産状況を取得する
        """
        pass
