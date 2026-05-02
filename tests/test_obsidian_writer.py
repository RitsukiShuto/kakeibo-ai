import os
import pytest
from src.output.obsidian_writer import ObsidianWriter

@pytest.fixture
def writer(tmp_path, monkeypatch):
    # tmp_path を Vault パスとして環境変数をモック
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))
    monkeypatch.setenv("OBSIDIAN_REPORT_DIR", "Reviews/Kakeibo")
    return ObsidianWriter()

def test_write_report_and_index(writer, tmp_path):
    content = "# Test Report"
    filepath = writer.write_report(content)
    
    # 1. ファイルが作成されたか
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        assert f.read() == content

    # 2. フォルダ階層が正しいか (target_root/Year/Month/file)
    # デフォルトの target_root は tmp_path + Reviews/Kakeibo
    assert "Reviews" in filepath
    assert "Kakeibo" in filepath

    # 3. インデックスファイルが作成されたか
    index_path = os.path.join(writer.target_root, "Kakeibo_Index.md")
    assert os.path.exists(index_path)
    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()
        assert "# 📑 家計簿AIレビュー インデックス" in index_content
        assert "家計簿レビュー" in index_content
