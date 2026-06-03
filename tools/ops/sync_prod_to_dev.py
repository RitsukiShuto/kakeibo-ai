#!/usr/bin/env python3
import sqlite3
import os
import shutil
import sys
from pathlib import Path

def sync_prod_to_dev():
    """
    Synchronizes production data to the local development environment (local/kakeibo.db)
    with strict anonymization of sensitive personal information.
    """
    print("=== Production to Development Data Sync Tool ===")

    # 1. Path Resolution
    env_prod_db = os.getenv("PROD_DB_PATH")
    
    if env_prod_db:
        prod_db_path = Path(env_prod_db).absolute()
    elif Path("prod_local/kakeibo.db").exists():
        prod_db_path = Path("prod_local/kakeibo.db").absolute()
    elif Path("../kakeibo-ai/prod_local/kakeibo.db").exists():
        prod_db_path = Path("../kakeibo-ai/prod_local/kakeibo.db").absolute()
    else:
        # Fallback if no prod_local found, assume it might be in local/ (dangerous if running on prod)
        prod_db_path = Path("local/kakeibo.db").absolute()
    
    env_dev_db = os.getenv("KAKEIBO_DB_PATH")
    if env_dev_db:
        dev_db_path = Path(env_dev_db).absolute()
    else:
        dev_db_path = Path("local/kakeibo.db").absolute()

    print(f"Source (Prod): {prod_db_path}")
    print(f"Destination (Dev): {dev_db_path}")

    # 2. Safety Guards
    if not prod_db_path.exists():
        print(f"Error: Production database not found at {prod_db_path}")
        return

    if prod_db_path == dev_db_path:
        # If they are the same, it might mean we are on a production machine
        # or the paths are just pointing to the same file.
        print("Error: Source and destination are the same!")
        print("Safety check triggered: You cannot sync the database to itself.")
        print("If you are in production, THIS IS NOT ALLOWED.")
        return

    # Check for production environment markers
    if os.path.exists("/etc/rpi-issue") or os.getenv("ENVIRONMENT") == "production":
         if "--force" not in sys.argv:
             print("Error: Potential production environment detected.")
             print("Use --force if you really want to run this here, but be extremely careful.")
             return

    # 3. Connect to production in read-only mode
    prod_uri = f"file:{prod_db_path}?mode=ro"
    try:
        prod_conn = sqlite3.connect(prod_uri, uri=True)
        prod_conn.row_factory = sqlite3.Row
    except sqlite3.OperationalError as e:
        print(f"Error connecting to production DB: {e}")
        return

    # 4. Connect to dev (will create/overwrite)
    if dev_db_path.exists():
        print("Development database already exists. Overwriting...")
        dev_db_path.unlink()
    
    # Ensure local directory exists
    dev_db_path.parent.mkdir(parents=True, exist_ok=True)
    
    dev_conn = sqlite3.connect(dev_db_path)
    dev_cursor = dev_conn.cursor()

    # 5. Replicate Schema
    cursor = prod_conn.cursor()
    cursor.execute("SELECT sql, name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        if table['sql'] and not table['name'].startswith('sqlite_'):
            dev_cursor.execute(table['sql'])
    dev_conn.commit()

    # 6. Synchronize and Anonymize Data
    print("Synchronizing and anonymizing transactions...")
    cursor.execute("SELECT * FROM transactions")
    tx_count = 0
    for row in cursor:
        data = dict(row)
        # Strict Anonymization
        category = data.get('category') or "Unknown"
        anonymized_text = f"Store [{category}]"
        
        if 'comment' in data:
            data['comment'] = anonymized_text
        if 'content' in data:
            # Although not in schema, keep for parity with staging sync
            data['content'] = anonymized_text
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        dev_cursor.execute(f"INSERT INTO transactions ({columns}) VALUES ({placeholders})", list(data.values()))
        tx_count += 1
    
    print(f"  Synced {tx_count} transactions.")

    print("Synchronizing and anonymizing assets...")
    cursor.execute("SELECT * FROM assets")
    asset_count = 0
    for row in cursor:
        data = dict(row)
        # Anonymization: institution -> Institution [StableHash]
        original_inst = data.get('institution')
        if original_inst:
            # Use a simple stable hash-like value for the ID
            inst_id = sum(ord(c) for c in original_inst) % 1000
            data['institution'] = f"Institution {inst_id}"
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        dev_cursor.execute(f"INSERT INTO assets ({columns}) VALUES ({placeholders})", list(data.values()))
        asset_count += 1
    print(f"  Synced {asset_count} assets.")

    print("Synchronizing analysis history (masked)...")
    cursor.execute("SELECT * FROM analysis_history")
    ah_count = 0
    for row in cursor:
        data = dict(row)
        data['summary'] = "Anonymized summary for development."
        if 'raw_response' in data:
            data['raw_response'] = "{}"
        if 'report_path' in data:
            data['report_path'] = "/tmp/anonymized_report.md"
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        dev_cursor.execute(f"INSERT INTO analysis_history ({columns}) VALUES ({placeholders})", list(data.values()))
        ah_count += 1
    print(f"  Synced {ah_count} analysis history records.")

    print("Synchronizing system status...")
    cursor.execute("SELECT * FROM system_status")
    for row in cursor:
        data = dict(row)
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        dev_cursor.execute(f"INSERT INTO system_status ({columns}) VALUES ({placeholders})", list(data.values()))

    dev_conn.commit()
    
    # Sync configs
    sync_configs(prod_db_path.parent / "config", dev_db_path.parent / "config")

    dev_conn.close()
    prod_conn.close()
    print("Sync complete.")
    
    verify_sync(dev_db_path)

def sync_configs(src_dir, dest_dir):
    if not src_dir.exists():
        return
    
    print(f"Synchronizing configs from {src_dir}...")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for config_file in src_dir.glob("*.json"):
        dest_file = dest_dir / config_file.name
        if not dest_file.exists():
            print(f"  Copying {config_file.name}...")
            shutil.copy(config_file, dest_file)
        else:
            print(f"  {config_file.name} already exists in local. Skipping.")

def verify_sync(db_path):
    print("\n--- Verification ---")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT comment, category FROM transactions LIMIT 5")
    print("Sample Transactions (Anonymized):")
    for row in cursor:
        print(f"  Category: {row['category']}, Comment: {row['comment']}")
        if "Store [" not in row['comment']:
             print("  Warning: Transaction comment might not be anonymized correctly!")

    cursor.execute("SELECT institution FROM assets LIMIT 5")
    print("Sample Assets (Anonymized):")
    for row in cursor:
        print(f"  Institution: {row['institution']}")
    
    conn.close()
    print("Verification finished.")

if __name__ == "__main__":
    sync_prod_to_dev()
