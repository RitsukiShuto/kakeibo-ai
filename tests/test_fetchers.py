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
        # キーワード定義
        KEYWORD_ITEM = "\u9805\u76ee" # 項目
        KEYWORD_VALUATION = "\u8a55\u4fa1\u984d" # 評価額
        BANK_NAME = "\u30c6\u30b9\u30c8\u9280\u884c" # テスト銀行
        AMOUNT_STR = "123,456\u5186" # 123,456円

        # ヘッダーの作成 (2列構成: 項目, 評価額)
        mock_th_item = MagicMock()
        mock_th_item.inner_text.return_value = KEYWORD_ITEM
        mock_th_val = MagicMock()
        mock_th_val.inner_text.return_value = KEYWORD_VALUATION
        
        # データ行の作成
        mock_td_name = MagicMock()
        mock_td_name.inner_text.return_value = BANK_NAME
        mock_td_amount = MagicMock()
        mock_td_amount.inner_text.return_value = AMOUNT_STR
        
        mock_row = MagicMock()
        mock_row.query_selector_all.return_value = [mock_td_name, mock_td_amount]
        mock_row.query_selector.return_value = None 
        mock_row.get_attribute.return_value = ""
        
        mock_table = MagicMock()
        def table_qsa_handler(selector):
            if selector == 'th': return [mock_th_item, mock_th_val]
            if selector == 'tr': return [mock_row]
            return []
        mock_table.query_selector_all.side_effect = table_qsa_handler
        
        mock_section = MagicMock()
        mock_section.query_selector_all.return_value = [mock_table]
        def page_qs_handler(selector):
            if selector == "section#portfolio_det_depo":
                return mock_section
            return None
        mock_page.query_selector.side_effect = page_qs_handler

        assets = fetcher.fetch_assets(headless=True)

        
        assert len(assets) == 1
        assert assets[0].amount == 123456
        assert assets[0].institution == BANK_NAME

@patch('src.fetcher.moneyforward_fetcher.pd.read_csv')
def test_mf_parse_csv(mock_read_csv, mock_mf_env):
    fetcher = MoneyForwardFetcher()
    # 日本語カラム名の文字化け対策
    df = pd.DataFrame({
        "ID": ["1"],
        "\u65e5\u4ed8": ["2024/01/01"], # 日付
        "\u5185\u5bb9": ["test"], # 内容
        "\u91d1\u984d": ["-1000"], # 金額
        "\u5927\u9805\u76ee": ["food"], # 大項目
        "\u4e2d\u9805\u76ee": ["lunch"], # 中項目
        "\u8a08\u7b97\u5bfe\u8c61": ["1"] # 計算対象
    })
    mock_read_csv.return_value = df
    transactions = fetcher._parse_csv("dummy.csv")
    assert len(transactions) == 1
    assert transactions[0].amount == 1000

# ==========================================
# Zaim Fetcher Tests
# ==========================================

@patch('src.fetcher.zaim_fetcher.ZaimAPI')
def test_zaim_fetcher_success(mock_zaim_api, mock_zaim_env):
    mock_instance = mock_zaim_api.return_value
    mock_instance.category.return_value = [{'id': 1, 'name': 'cat'}]
    mock_instance.genre.return_value = [{'id': 1, 'name': 'gen'}]
    mock_instance.data.return_value = [
        {'id': 1, 'date': '2024-01-01', 'category_id': 1, 'genre_id': 1, 'amount': 100, 'mode': 'payment', 'comment': ''}
    ]
    
    fetcher = ZaimFetcher()
    transactions = fetcher.fetch_transactions()
    assert len(transactions) == 1

@patch('src.fetcher.zaim_fetcher.ZaimAPI')
def test_zaim_fetch_assets(mock_zaim_api, mock_zaim_env):
    mock_instance = mock_zaim_api.return_value
    mock_instance.account.return_value = [
        {'id': 1, 'name': 'wallet', 'balance': 5000, 'active': 1}
    ]
    fetcher = ZaimFetcher()
    assets = fetcher.fetch_assets()
    assert len(assets) == 1
    assert assets[0].amount == 5000
