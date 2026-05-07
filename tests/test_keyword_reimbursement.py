import os
import pandas as pd
from datetime import datetime
from src.fetcher.moneyforward_fetcher import MoneyForwardFetcher

def test_keyword_auto_reimbursement():
    # テスト用のダミーCSVを作成
    csv_path = "data/csv/test_keywords.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    data = {
        "ID": ["1", "2", "3", "4"],
        "日付": ["2026/05/01", "2026/05/02", "2026/05/03", "2026/05/04"],
        "内容": ["通常のご飯", "飲み会立替", "交通費経費精算", "普通の買い物"],
        "金額": ["-1000", "-20000", "-500", "-3000"],
        "大項目": ["食費", "食費", "交通費", "日用品"],
        "中項目": ["昼食", "飲み会", "電車", "雑貨"],
        "計算対象": ["1", "1", "1", "1"]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False, encoding="cp932")
    
    fetcher = MoneyForwardFetcher()
    transactions = fetcher._parse_csv(csv_path)
    
    # 検証
    # 1. 通常
    assert transactions[0].is_reimbursement == 0
    assert transactions[0].self_amount is None
    
    # 2. 立替
    assert transactions[1].is_reimbursement == 1
    assert transactions[1].self_amount == 0
    assert transactions[1].reimbursement_status == "pending"
    
    # 3. 経費精算
    assert transactions[2].is_reimbursement == 1
    assert transactions[2].self_amount == 0
    assert transactions[2].reimbursement_status == "pending"
    
    # 4. 通常
    assert transactions[3].is_reimbursement == 0
    
    print("✅ Keyword auto reimbursement test passed!")
    
    if os.path.exists(csv_path):
        os.remove(csv_path)

if __name__ == "__main__":
    test_keyword_auto_reimbursement()
