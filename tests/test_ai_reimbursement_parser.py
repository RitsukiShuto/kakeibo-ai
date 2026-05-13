import os
from unittest.mock import MagicMock, patch
from src.analyzer.gemini_analyzer import GeminiAnalyzer

def test_parse_reimbursement_text(mocker):
    # Providerのモックを作成
    mock_provider = MagicMock()
    
    # generate_contentの戻り値を設定
    mock_provider.generate_content.side_effect = [
        '{"self_amount": 5000, "reason": "test"}',
        '{"self_amount": 5000, "reason": "test"}',
        '{"self_amount": 0, "reason": "test"}'
    ]
    mock_provider.get_model_name.return_value = "gemini-2.0-flash"
    
    # LLMFactory.create_providerをパッチしてモックProviderを返すようにする
    mocker.patch('src.analyzer.providers.factory.LLMFactory.create_provider', return_value=mock_provider)

    # Ensure environment variables are set
    mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "dummy", "LLM_PROVIDER": "gemini"})

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
