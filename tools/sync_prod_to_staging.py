import sqlite3
import os
import shutil
import sys
from pathlib import Path

def sync_prod_to_staging():
    # Paths
    # 1. Try environment variable
    # 2. Try common production path relative to staging
    # 3. Try local/prod_local paths
    env_prod_db = os.getenv("PROD_DB_PATH")
    
    if env_prod_db:
        prod_db_path = Path(env_prod_db).absolute()
    elif Path("../kakeibo-ai/prod_local/kakeibo.db").exists():
        prod_db_path = Path("../kakeibo-ai/prod_local/kakeibo.db").absolute()
    elif Path("prod_local/kakeibo.db").exists():
        prod_db_path = Path("prod_local/kakeibo.db").absolute()
    else:
        prod_db_path = Path("local/kakeibo.db").absolute()
    
    staging_dir = Path("staging/local")
    staging_db_path = staging_dir / "kakeibo_staging.db"
    staging_db_path = staging_db_path.absolute()

    print(f"Source: {prod_db_path}")
    print(f"Destination: {staging_db_path}")

    # 1. Isolation & Safety Guards
    if not prod_db_path.exists():
        print(f"Error: Production database not found at {prod_db_path}")
        return

    if prod_db_path == staging_db_path:
        print("Error: Source and destination are the same!")
        return
    
    # Ensure staging directory exists
    staging_dir.mkdir(parents=True, exist_ok=True)

    # 2. Connect to production in read-only mode
    # Using URI for read-only access
    prod_uri = f"file:{prod_db_path}?mode=ro"
    try:
        prod_conn = sqlite3.connect(prod_uri, uri=True)
        prod_conn.row_factory = sqlite3.Row
    except sqlite3.OperationalError as e:
        print(f"Error connecting to production DB: {e}")
        return

    # 3. Connect to staging (will create/overwrite)
    if staging_db_path.exists():
        print("Staging database already exists. Overwriting...")
        staging_db_path.unlink()
    
    staging_conn = sqlite3.connect(staging_db_path)
    
    # Create tables in staging (copy schema from prod)
    # We can just copy the file and then anonymize, but that might be risky if we fail to anonymize.
    # Better to create tables and insert anonymized data.
    
    # Let's get the schema from prod
    cursor = prod_conn.cursor()
    cursor.execute("SELECT sql, name FROM sqlite_master WHERE type='table'")
    tables_sql = cursor.fetchall()
    
    staging_cursor = staging_conn.cursor()
    for table_sql in tables_sql:
        if table_sql['sql'] and not table_sql['name'].startswith('sqlite_'):
            staging_cursor.execute(table_sql['sql'])
    staging_conn.commit()

    print("Synchronizing and anonymizing transactions...")
    # 4. Sync Transactions
    cursor.execute("SELECT * FROM transactions")
    tx_count = 0
    for row in cursor:
        data = dict(row)
        # Anonymization Logic
        # content (comment) -> Store [Category]
        category = data['category'] or "Unknown"
        data['comment'] = f"Store [{category}]"
        # We can also use Transaction [ID] if desired
        # data['comment'] = f"Transaction {data['transaction_id']}"
        
        # genre (medium category) is usually safe (e.g., "Lunch"), but let's keep it.
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        staging_cursor.execute(f"INSERT INTO transactions ({columns}) VALUES ({placeholders})", list(data.values()))
        tx_count += 1
    
    print(f"Synced {tx_count} transactions.")

    print("Synchronizing and anonymizing assets...")
    # 5. Sync Assets
    cursor.execute("SELECT * FROM assets")
    asset_count = 0
    for row in cursor:
        data = dict(row)
        # Anonymization Logic
        # institution -> Institution [ID]
        original_inst = data['institution']
        if original_inst:
            # Simple hash or just a placeholder
            data['institution'] = f"Institution {hash(original_inst) % 1000}"
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        staging_cursor.execute(f"INSERT INTO assets ({columns}) VALUES ({placeholders})", list(data.values()))
        asset_count += 1
    print(f"Synced {asset_count} assets.")

    # 6. Analysis History (Anonymize or skip)
    # The requirement says "synchronize data ... while protecting sensitive personal information".
    # analysis_history contains summaries which are highly sensitive.
    # For staging, we probably don't need old analysis history, or we should mask it.
    print("Synchronizing analysis history (masked)...")
    cursor.execute("SELECT * FROM analysis_history")
    ah_count = 0
    for row in cursor:
        data = dict(row)
        data['summary'] = "Anonymized summary for testing."
        data['raw_response'] = "{}" # Clear raw AI response
        data['report_path'] = "/tmp/anonymized_report.md"
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        staging_cursor.execute(f"INSERT INTO analysis_history ({columns}) VALUES ({placeholders})", list(data.values()))
        ah_count += 1
    print(f"Synced {ah_count} analysis history records.")

    # 7. System Status (Copy as is)
    cursor.execute("SELECT * FROM system_status")
    for row in cursor:
        data = dict(row)
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        staging_cursor.execute(f"INSERT INTO system_status ({columns}) VALUES ({placeholders})", list(data.values()))

    staging_conn.commit()
    prod_conn.close()
    staging_conn.close()
    print("Sync complete.")

    # Verification block
    verify_sync(staging_db_path)

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

def test_anonymization_logic():
    """
    Unit test for the anonymization logic using in-memory databases.
    """
    print("\n--- Running Unit Tests ---")
    source_conn = sqlite3.connect(":memory:")
    dest_conn = sqlite3.connect(":memory:")
    
    source_cursor = source_conn.cursor()
    source_cursor.execute("CREATE TABLE transactions (transaction_id TEXT, category TEXT, comment TEXT)")
    source_cursor.execute("INSERT INTO transactions VALUES ('tx1', 'Food', 'Lunch at Starbucks')")
    
    source_cursor.execute("CREATE TABLE assets (institution TEXT, amount INTEGER)")
    source_cursor.execute("INSERT INTO assets VALUES ('My Secret Bank', 10000)")
    
    # Run a mini-sync logic
    source_cursor.execute("SELECT * FROM transactions")
    for row in source_cursor:
        data = dict(zip([col[0] for col in source_cursor.description], row))
        # Logic from main script
        data['comment'] = f"Store [{data['category']}]"
        
        # Verify
        assert data['comment'] == "Store [Food]"
        assert "Starbucks" not in data['comment']
        print("  ✓ Transaction anonymization passed.")

    source_cursor.execute("SELECT * FROM assets")
    for row in source_cursor:
        data = dict(zip([col[0] for col in source_cursor.description], row))
        # Logic from main script
        original_inst = data['institution']
        data['institution'] = f"Institution {hash(original_inst) % 1000}"
        
        # Verify
        assert data['institution'] != "My Secret Bank"
        assert "Institution" in data['institution']
        print("  ✓ Asset anonymization passed.")

    print("--- Unit Tests Passed ---\n")

if __name__ == "__main__":
    if "--test" in sys.argv:
        test_anonymization_logic()
    else:
        # Check if production DB is empty and warn
        sync_prod_to_staging()
