import os
from src.analyzer.gemini_analyzer import GeminiAnalyzer

def test_parse_reimbursement_text():
    analyzer = GeminiAnalyzer()
    
    # 1. シンプルな割り勘
    res1 = analyzer.parse_reimbursement_text("4人で割り勘", 20000)
    assert res1 is not None
    assert res1["self_amount"] == 5000
    
    # 2. 自己負担指定
    res2 = analyzer.parse_reimbursement_text("総額20000円だけど、自分は酒飲んでないから5000円でいいよって言われた", 20000)
    assert res2 is not None
    assert res2["self_amount"] == 5000
    
    # 3. 経費（全額立替）
    res3 = analyzer.parse_reimbursement_text("全額経費で落ちるはず", 1500)
    assert res3 is not None
    assert res3["self_amount"] == 0
    
    print("✅ AI parse reimbursement text test passed!")

if __name__ == "__main__":
    test_parse_reimbursement_text()
