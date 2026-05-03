import pytest
import os
import pandas as pd
from datetime import date
from unittest.mock import MagicMock, patch, mock_open
from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher
from src.fetcher.zaim_fetcher import ZaimFetcher
from src.models import Transaction, Asset

@pytest.fixture
def mock_mf_env():
    with patch.dict('os.environ', {'MF_USER_ID': 'test_user', 'MF_PASSWORD': 'test_password'}):
        yield

@pytest.fixture
def mock_zaim_env():
    with patch.dict('os.environ', {
        "ZAIM_CONSUMER_ID": "test",
        "ZAIM_CONSUMER_SECRET": "test",
        "ZAIM_ACCESS_TOKEN": "test",
        "ZAIM_ACCESS_TOKEN_SECRET": "test"
    }):
        yield

# ==========================================
# MoneyForward Fetcher Tests
# ==========================================

def setup_mock_playwright(mock_playwright):
    mock_p = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_context = MagicMock()
    mock_p.chromium.launch_persistent_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.pages = [mock_page]
    mock_context.new_page.return_value = mock_page
    return mock_p, mock_context, mock_page

@patch('src.fetcher.moneyforward_fetcher.sync_playwright')
def test_mf_login_success(mock_playwright, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    _, _, mock_page = setup_mock_playwright(mock_playwright)
    
    mock_page.url = "https://moneyforward.com/users/sign_in"
    mock_update_btn = MagicMock()
    mock_update_btn.is_visible.return_value = True
    mock_page.locator.return_value.first = mock_update_btn
    mock_page.query_selector_all.return_value = [] # no updating items
    
    result = fetcher._login_and_update(mock_page, headless=True)
    assert result is True

@patch('src.fetcher.moneyforward_fetcher.sync_playwright')
def test_mf_login_fail(mock_playwright, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    _, _, mock_page = setup_mock_playwright(mock_playwright)
    mock_page.url = "https://moneyforward.com/users/sign_in"
    mock_page.fill.side_effect = Exception("Login Error")
    
    result = fetcher._login_and_update(mock_page, headless=True)
    assert result is False

@patch('src.fetcher.moneyforward_fetcher.sync_playwright')
def test_mf_fetch_transactions(mock_playwright, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    _, mock_context, mock_page = setup_mock_playwright(mock_playwright)
    
    with patch.object(fetcher, '_login_and_update', return_value=True):
        with patch.object(fetcher, '_parse_csv', return_value=[Transaction(transaction_date=date(2024,1,1), category="C", amount=1, source="MF", mode="payment")]):
            mock_download = MagicMock()
            mock_download.value = MagicMock()
            mock_page.expect_download.return_value.__enter__.return_value = mock_download
            
            transactions = fetcher.fetch_transactions(headless=True)
            assert len(transactions) == 1

@patch('src.fetcher.moneyforward_fetcher.sync_playwright')
def test_mf_fetch_transactions_login_fail(mock_playwright, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    _, mock_context, mock_page = setup_mock_playwright(mock_playwright)
    with patch.object(fetcher, '_login_and_update', return_value=False):
        transactions = fetcher.fetch_transactions(headless=True)
        assert transactions == []

@patch('src.fetcher.moneyforward_fetcher.sync_playwright')
def test_mf_fetch_assets(mock_playwright, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    _, mock_context, mock_page = setup_mock_playwright(mock_playwright)
    
    with patch.object(fetcher, '_login_and_update', return_value=True):
        mock_section = MagicMock()
        mock_table = MagicMock()
        mock_th1 = MagicMock()
        mock_th1.inner_text.return_value = "評価額"
        mock_table.query_selector_all.side_effect = [
            [mock_th1], # headers
            [MagicMock()] # rows (need to mock query_selector for td)
        ]
        mock_td1 = MagicMock()
        mock_td1.inner_text.return_value = "銀行"
        mock_td2 = MagicMock()
        mock_td2.inner_text.return_value = "10,000円"
        
        mock_row = MagicMock()
        mock_row.query_selector_all.return_value = [mock_td1, mock_td2]
        mock_row.query_selector.return_value = None # not a th row
        mock_row.get_attribute.return_value = ""
        
        mock_table.query_selector_all.side_effect = [ [mock_th1], [mock_row] ]
        mock_section.query_selector_all.return_value = [mock_table]
        mock_page.query_selector.return_value = mock_section

        assets = fetcher.fetch_assets(headless=True)
        assert len(assets) == 1
        assert assets[0].amount == 10000

@patch('src.fetcher.moneyforward_fetcher.pd.read_csv')
def test_mf_parse_csv(mock_read_csv, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    df = pd.DataFrame({
        "ID": ["1"],
        "日付": ["2024/01/01"],
        "内容": ["テスト"],
        "金額": ["-1000"],
        "大項目": ["食費"],
        "中項目": ["外食"],
        "計算対象": ["1"]
    })
    mock_read_csv.return_value = df
    transactions = fetcher._parse_csv("dummy.csv")
    assert len(transactions) == 1
    assert transactions[0].amount == 1000
    assert transactions[0].mode == "payment"

# ==========================================
# Zaim Fetcher Tests
# ==========================================

@patch('src.fetcher.zaim_fetcher.ZaimAPI')
def test_zaim_fetcher_success(mock_zaim_api, mock_zaim_env):
    mock_instance = mock_zaim_api.return_value
    mock_instance.category.return_value = [{'id': 101, 'name': '食費'}]
    mock_instance.genre.return_value = [{'id': 10101, 'name': '外食'}]
    mock_instance.data.return_value = [
        {'id': 1, 'date': '2024-01-01', 'category_id': 101, 'genre_id': 10101, 'amount': 100, 'mode': 'payment', 'comment': 'test'}
    ]
    
    fetcher = ZaimFetcher()
    transactions = fetcher.fetch_transactions()
    assert len(transactions) == 1
    assert transactions[0].category == "食費"
    assert transactions[0].genre == "外食"

def test_zaim_fetch_assets(mock_zaim_env):
    fetcher = ZaimFetcher()
    with pytest.raises(NotImplementedError):
        fetcher.fetch_assets()
