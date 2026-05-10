import pytest
import os
import pandas as pd
import json
from datetime import date
from unittest.mock import MagicMock, patch
from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher
from src.fetcher.zaim_fetcher import ZaimFetcher
from src.models import Transaction

@pytest.fixture
def mapping_file():
    mapping_data = {
        "category_mappings": {
            "未分類": "その他"
        },
        "genre_mappings": {
            "ランチ": {
                "category": "食費",
                "genre": "昼食"
            },
            "コンビニ": "日用品"
        }
    }
    mapping_path = "local/config/mapping_test.json"
    os.makedirs(os.path.dirname(mapping_path), exist_ok=True)
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping_data, f)
    yield mapping_path
    if os.path.exists(mapping_path):
        os.remove(mapping_path)

@patch('src.fetcher.moneyforward_fetcher.pd.read_csv')
def test_mf_mapping_integration(mock_read_csv, mapping_file):
    with patch('src.utils.category_mapper.CategoryMapper.__init__', lambda self, path=mapping_file: setattr(self, 'mapping_path', path) or setattr(self, 'mapping', self._load_mapping())):
        fetcher = MoneyForwardFetcher()
        # カラム名の定義（MoneyForwardFetcher内の検索ロジックに合わせる）
        df = pd.DataFrame({
            "ID": ["1", "2", "3"],
            "日付": ["2024/01/01", "2024/01/02", "2024/01/03"],
            "内容": ["test1", "test2", "test3"],
            "金額": ["-1000", "-500", "-2000"],
            "大項目": ["未分類", "食費", "食費"],
            "中項目": ["", "ランチ", "コンビニ"],
            "計算対象": ["1", "1", "1"]
        })
        mock_read_csv.return_value = df
        
        transactions = fetcher._parse_csv("dummy.csv")
        
        # 未分類 -> その他 (category mapping)
        assert transactions[0].category == "その他"
        
        # ランチ -> 食費/昼食 (genre mapping with category override)
        assert transactions[1].category == "食費"
        assert transactions[1].genre == "昼食"
        
        # コンビニ -> 日用品 (genre mapping string style)
        assert transactions[2].genre == "日用品"

@patch('src.fetcher.zaim_fetcher.ZaimAPI')
def test_zaim_mapping_integration(mock_zaim_api, mapping_file):
    env_vars = {
        "ZAIM_CONSUMER_ID": "test_id",
        "ZAIM_CONSUMER_SECRET": "test_secret",
        "ZAIM_ACCESS_TOKEN": "test_token",
        "ZAIM_ACCESS_TOKEN_SECRET": "test_token_secret"
    }
    with patch.dict('os.environ', env_vars):
        with patch('src.utils.category_mapper.CategoryMapper.__init__', lambda self, path=mapping_file: setattr(self, 'mapping_path', path) or setattr(self, 'mapping', self._load_mapping())):
            mock_instance = mock_zaim_api.return_value
            mock_instance.category.return_value = [
                {'id': 1, 'name': '未分類'},
                {'id': 2, 'name': '食費'}
            ]
            mock_instance.genre.return_value = [
                {'id': 11, 'name': 'ランチ'},
                {'id': 12, 'name': 'コンビニ'}
            ]
            mock_instance.data.return_value = [
                {'id': 1, 'date': '2024-01-01', 'category_id': 1, 'genre_id': 0, 'amount': 100, 'mode': 'payment', 'comment': ''},
                {'id': 2, 'date': '2024-01-02', 'category_id': 2, 'genre_id': 11, 'amount': 200, 'mode': 'payment', 'comment': ''},
                {'id': 3, 'date': '2024-01-03', 'category_id': 2, 'genre_id': 12, 'amount': 300, 'mode': 'payment', 'comment': ''}
            ]
            
            fetcher = ZaimFetcher()
            transactions = fetcher.fetch_transactions()
            
            # 未分類 -> その他
            assert transactions[0].category == "その他"
            
            # ランチ -> 食費/昼食
            assert transactions[1].category == "食費"
            assert transactions[1].genre == "昼食"
            
            # コンビニ -> 日用品
            assert transactions[2].genre == "日用品"
