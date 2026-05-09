import os
from unittest.mock import MagicMock
from src.analyzer.gemini_analyzer import GeminiAnalyzer

def test_parse_reimbursement_text(mocker):
    mock_response_1 = MagicMock()
    mock_response_1.text = '{"self_amount": 5000, "reason": "test"}'
    
    mock_response_2 = MagicMock()
    mock_response_2.text = '{"self_amount": 5000, "reason": "test"}'
    
    mock_response_3 = MagicMock()
    mock_response_3.text = '{"self_amount": 0, "reason": "test"}'
    
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.side_effect = [
        mock_response_1,
        mock_response_2,
        mock_response_3
    ]
    mocker.patch('src.analyzer.gemini_analyzer.genai.Client', return_value=mock_client_instance)

    # Ensure GEMINI_API_KEY is set so __init__ doesn't fail
    mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"})

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
