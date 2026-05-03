import pytest
import os
import sqlite3
from src.output.visualizer import Visualizer
from src.db.database import Database
from src.models import Asset
from datetime import date

def test_generate_asset_trend_graph(tmp_path):
    # Setup temporary DB
    db_file = tmp_path / "test_kakeibo.db"
    db = Database(db_path=str(db_file))
    
    # Insert mock data
    assets = [
        Asset(acquired_date=date(2024, 1, 1), asset_type="預金", amount=100000, source="test"),
        Asset(acquired_date=date(2024, 1, 1), asset_type="投資信託", amount=50000, source="test"),
        Asset(acquired_date=date(2024, 2, 1), asset_type="預金", amount=110000, source="test"),
        Asset(acquired_date=date(2024, 2, 1), asset_type="投資信託", amount=60000, source="test")
    ]
    db.save_assets(assets)

    # Initialize Visualizer with a temporary output dir
    output_dir = tmp_path / "graphs"
    visualizer = Visualizer(output_dir=str(output_dir))
    
    # Generate graph
    graph_path = visualizer.generate_asset_trend_graph(db_path=str(db_file))
    
    assert graph_path != ""
    assert os.path.exists(graph_path)
    assert graph_path.endswith(".png")

def test_generate_asset_trend_graph_empty_db(tmp_path):
    db_file = tmp_path / "empty.db"
    db = Database(db_path=str(db_file))
    
    visualizer = Visualizer(output_dir=str(tmp_path))
    graph_path = visualizer.generate_asset_trend_graph(db_path=str(db_file))
    
    assert graph_path == ""
