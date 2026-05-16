import os
import time
import logging
import pandas as pd
from datetime import datetime, date
from typing import List, Optional
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from src.models import Transaction, Asset
from src.fetcher.base_fetcher import BaseFetcher
from src.utils.category_mapper import CategoryMapper
from src.utils.logger import logger

load_dotenv(os.path.join(os.getenv("KAKEIBO_LOCAL_DIR", "local"), ".env"))

class MoneyForwardFetcher(BaseFetcher):
    def __init__(self):
        self.user_id = os.getenv("MF_USER_ID")
        self.password = os.getenv("MF_PASSWORD")
        local_dir = os.getenv("KAKEIBO_LOCAL_DIR", "local")
        self.user_data_dir = os.path.join(os.getcwd(), local_dir, "mf_session")
        self.mapper = CategoryMapper()

    def _login_and_update(self, page, headless: bool):
        logger.info("Navigating to sign_in page...")
        page.goto("https://moneyforward.com/users/sign_in")
        
        if "sign_in" in page.url:
            if not headless:
                logger.warning("--- SETUP MODE --- Please complete login in the browser.")
                page.wait_for_url("https://moneyforward.com/", timeout=300000)
            else:
                logger.info("Logging in to MoneyForward...")
                try:
                    page.fill('input[name="user[email]"]', self.user_id)
                    page.click('input[type="submit"]')
                    page.fill('input[name="user[password]"]', self.password)
                    page.click('input[type="submit"]')
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Auto login failed: {e}")
                    return False

        logger.info("Updating financial data...")
        page.goto("https://moneyforward.com/", wait_until="networkidle")
        try:
            update_button = page.locator('button:has-text("金融機関からのデータ一括更新"), a:has-text("金融機関からのデータ一括更新"), button:has-text("一括更新"), a:has-text("一括更新")').first
            if update_button.is_visible():
                update_button.click()
                time.sleep(2)
        except Exception as e:
            logger.warning(f"Update button click failed: {e}")

        # 3. 更新完了を監視
        page.goto("https://moneyforward.com/accounts", wait_until="networkidle")
        start_time = time.time()
        while time.time() - start_time < 300:
            try:
                # ページの状態が落ち着くまで少し待機
                time.sleep(5)
                updating_elements = page.query_selector_all('section#account-table td:has-text("更新中")')
                if len(updating_elements) == 0:
                    logger.info("All accounts updated.")
                    break
                logger.info(f"Waiting for {len(updating_elements)} accounts to update...")
            except Exception as e:
                logger.warning(f"Error during update check (might be navigating): {e}")
            
            time.sleep(30)
            try:
                page.reload(wait_until="networkidle")
            except Exception as e:
                logger.warning(f"Reload failed: {e}")
        
        return True

    def fetch_transactions(self, headless: bool = True) -> List[Transaction]:
        logger.info(f"Starting MF transaction fetch (headless={headless})")
        with sync_playwright() as p:
            browser_context = self._launch_browser(p, headless)
            page = browser_context.new_page()
            
            if not self._login_and_update(page, headless):
                browser_context.close()
                return []

            page.goto("https://moneyforward.com/cf", wait_until="networkidle")
            time.sleep(5)

            try:
                dropdown_toggle = page.locator('a.dropdown-toggle:has-text("ダウンロード")')
                dropdown_toggle.click()
                time.sleep(1)

                csv_link_selector = '#js-csv-dl a'
                page.wait_for_selector(csv_link_selector, timeout=10000)
                
                with page.expect_download(timeout=60000) as download_info:
                    page.click(csv_link_selector)
                
                download = download_info.value
                csv_dir = os.path.join(os.getcwd(), "data", "csv")
                os.makedirs(csv_dir, exist_ok=True)
                csv_path = os.path.join(csv_dir, f"temp_mf_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
                download.save_as(csv_path)

                transactions = self._parse_csv(csv_path)
                browser_context.close()
                return transactions

            except Exception as e:
                logger.error(f"Failed to fetch transactions: {e}")
                browser_context.close()
                return []

    def fetch_historical_transactions(self, year: int, month: int, headless: bool = True, page=None) -> List[Transaction]:
        """
        指定された年月の明細データを取得する（直接URL指定方式）
        """
        logger.info(f"Starting MF historical fetch for {year}/{month}")
        
        # 外部からpageが渡されない場合は自前で起動
        if page is None:
            with sync_playwright() as p:
                browser_context = self._launch_browser(p, headless)
                page = browser_context.new_page()
                if not self._login_and_update(page, headless):
                    browser_context.close()
                    return []
                result = self._download_csv_direct(page, year, month)
                browser_context.close()
                return result
        else:
            return self._download_csv_direct(page, year, month)

    def _download_csv_direct(self, page, year: int, month: int) -> List[Transaction]:
        try:
            # CSVダウンロード用URLを直接叩く
            csv_url = f"https://moneyforward.com/cf/csv?month={month}&year={year}"
            logger.info(f"Downloading CSV directly from: {csv_url}")
            
            with page.expect_download(timeout=60000) as download_info:
                page.goto(csv_url)
            
            download = download_info.value
            csv_dir = os.path.join(os.getcwd(), "data", "csv")
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, f"history_mf_{year}{month:02d}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
            download.save_as(csv_path)

            return self._parse_csv(csv_path)
        except Exception as e:
            logger.error(f"Failed to download CSV for {year}/{month}: {e}")
            return []

    def fetch_assets(self, headless: bool = True) -> List[Asset]:
        logger.info(f"Starting MF asset fetch (headless={headless})")
        with sync_playwright() as p:
            browser_context = self._launch_browser(p, headless)
            page = browser_context.new_page()
            
            if not self._login_and_update(page, headless):
                browser_context.close()
                return []

            logger.info("Navigating to portfolio page...")
            page.goto("https://moneyforward.com/bs/portfolio", wait_until="networkidle")
            time.sleep(3)

            assets = []
            today = date.today()

            try:
                sections = {
                    "預金・現金": "section#portfolio_det_depo",
                    "株式": "section#portfolio_det_eq",
                    "投資信託": "section#portfolio_det_mf",
                    "年金": "section#portfolio_det_pns",
                    "ポイント": "section#portfolio_det_po",
                    "債券": "section#portfolio_det_bd",
                    "保険": "section#portfolio_det_ins",
                    "暗号資産": "section#portfolio_det_crypto",
                    "その他": "section#portfolio_det_oth"
                }

                for asset_type, selector in sections.items():
                    section = page.query_selector(selector)
                    if not section:
                        continue
                    
                    logger.info(f"--- Analyzing section: {asset_type} ---")
                    
                    # セクション内の各テーブルを処理
                    tables = section.query_selector_all('table.table-bordered')
                    for table in tables:
                        # 1. ヘッダーから「評価額」または「残高」の列インデックスを探す
                        headers = table.query_selector_all('th')
                        value_col_idx = -1
                        for i, th in enumerate(headers):
                            header_text = th.inner_text().strip()
                            if any(k in header_text for k in ["評価額", "残高", "現在の価値", "金額"]):
                                value_col_idx = i
                                break
                        
                        # ヘッダーが見つからない場合のフォールバック（預金などは2列目のことが多い）
                        if value_col_idx == -1:
                            value_col_idx = 1
                            logger.warning(f"  Value column not found in headers, falling back to index {value_col_idx}")

                        # 2. 各行のデータを取得
                        rows = table.query_selector_all('tr')
                        for row in rows:
                            if row.query_selector('th') or "total" in (row.get_attribute("class") or ""):
                                continue

                            cols = row.query_selector_all('td')
                            if len(cols) > value_col_idx:
                                name = cols[0].inner_text().strip().split('\n')[0]
                                amount_text = cols[value_col_idx].inner_text().strip().replace(',', '').replace('円', '')
                                
                                # 数値のみを抽出（カッコ内の数値などは無視）
                                amount_text = amount_text.split('(')[0].strip()
                                
                                try:
                                    if amount_text and amount_text.lstrip('-').isdigit():
                                        amount = int(amount_text)
                                        logger.debug(f"  Found asset: {name} = {amount:,}円 (at col {value_col_idx})")
                                        assets.append(Asset(
                                            acquired_date=today,
                                            asset_type=asset_type,
                                            amount=amount,
                                            source="MoneyForward",
                                            institution=name
                                        ))
                                except ValueError:
                                    continue

                browser_context.close()
                return assets

            except Exception as e:
                logger.error(f"Failed to fetch assets: {e}")
                browser_context.close()
                return []

    def _launch_browser(self, p, headless: bool):
        browser_context = p.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=headless,
            slow_mo=500,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars"]
        )
        page = browser_context.pages[0]
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return browser_context

    def get_session_cookies(self, headless: bool = True) -> dict:
        """
        PlaywrightのセッションからCookieを取得し、requests形式に変換する
        """
        logger.info("Extracting session cookies from Playwright...")
        with sync_playwright() as p:
            browser_context = self._launch_browser(p, headless)
            page = browser_context.pages[0]
            
            # ログイン状態を確認
            if not self._login_and_update(page, headless):
                browser_context.close()
                return {}

            cookies = browser_context.cookies()
            browser_context.close()
            
            # requests 用の辞書形式に変換
            cookie_dict = {c['name']: c['value'] for c in cookies}
            return cookie_dict

    def _parse_csv(self, csv_path: str) -> List[Transaction]:
        df = pd.read_csv(csv_path, encoding="cp932")
        
        def find_col(possible_names):
            for col in df.columns:
                if any(name in col for name in possible_names): return col
            return None

        col_id = find_col(["ID"])
        col_date = find_col(["日付"])
        col_content = find_col(["内容"])
        col_amount = find_col(["金額"])
        col_major = find_col(["大項目"])
        col_minor = find_col(["中項目"])
        col_calc = find_col(["計算対象"])

        transactions = []
        for _, row in df.iterrows():
            if col_calc and str(row[col_calc]) == "0": continue
            
            amount_val = str(row[col_amount]).replace(",", "")
            amount = int(float(amount_val))
            
            # 立替・経費の自動判定ロジック
            is_reimbursement = 0
            self_amount = None
            reimbursement_status = None
            comment_text = str(row[col_content]) if col_content else ""
            
            # キーワード判定
            reimbursement_keywords = ["立替", "精算", "経費"]
            if any(kw in comment_text for kw in reimbursement_keywords):
                is_reimbursement = 1
                self_amount = 0 # デフォルトで全額立替（経費精算待ち）として扱う
                reimbursement_status = "pending"

            raw_category = str(row[col_major]) if col_major else "未分類"
            raw_genre = str(row[col_minor]) if col_minor else ""
            
            # カテゴリマッピングの適用
            mapped_category, mapped_genre = self.mapper.apply_mapping(raw_category, raw_genre)

            transactions.append(Transaction(
                transaction_id=str(row[col_id]) if col_id else None,
                transaction_date=datetime.strptime(str(row[col_date]), "%Y/%m/%d").date(),
                category=mapped_category,
                genre=mapped_genre,
                amount=abs(amount),
                comment=comment_text,
                source="MoneyForward",
                mode="payment" if amount < 0 else "income",
                self_amount=self_amount,
                is_reimbursement=is_reimbursement,
                reimbursement_status=reimbursement_status
            ))
        return transactions
