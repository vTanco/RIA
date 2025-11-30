import sys
import os

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.database.session import engine as ria_engine, predatory_engine

def migrate_predatory_data():
    print("Starting migration of predatory journal data...")

    # 1. Check if source table exists in ria.db
    inspector = inspect(ria_engine)
    if "predatory_journals" not in inspector.get_table_names():
        print("Table 'predatory_journals' does not exist in ria.db. Nothing to migrate.")
        return

    # 2. Read data from ria.db
    with ria_engine.connect() as ria_conn:
        print("Reading data from ria.db...")
        result = ria_conn.execute(text("SELECT * FROM predatory_journals"))
        rows = result.fetchall()
        
        if not rows:
            print("No data found in 'predatory_journals' table in ria.db.")
            # Still drop the empty table
            ria_conn.execute(text("DROP TABLE predatory_journals"))
            print("Dropped empty 'predatory_journals' table from ria.db.")
            return

        print(f"Found {len(rows)} records to migrate.")
        
        # Get column names
        keys = result.keys()

    # 3. Write data to predatory.db
    # Ensure table exists (it should be created by main.py or we can force create here if needed, 
    # but let's assume the app initialization or models.py import handled it. 
    # Actually, since this is a script, we might need to ensure tables exist.)
    from backend.database.models import PredatoryJournal
    from backend.database.session import PredatoryBase
    PredatoryBase.metadata.create_all(bind=predatory_engine)

    with predatory_engine.connect() as pred_conn:
        print("Writing data to predatory.db...")
        # Prepare insert statement
        # We need to construct the INSERT statement dynamically or use SQLAlchemy Core
        
        # Simple approach: iterate and insert
        # Note: We might have ID conflicts if we preserve IDs, but usually safe to preserve for migration
        
        # Construct INSERT query
        columns = ", ".join(keys)
        placeholders = ", ".join([f":{k}" for k in keys])
        insert_sql = text(f"INSERT INTO predatory_journals ({columns}) VALUES ({placeholders})")
        
        for row in rows:
            # Convert row to dict
            row_dict = dict(zip(keys, row))
            try:
                pred_conn.execute(insert_sql, row_dict)
            except Exception as e:
                print(f"Error inserting row {row_dict.get('id')}: {e}")
        
        pred_conn.commit()
        print("Data migration complete.")

    # 4. Drop table from ria.db
    with ria_engine.connect() as ria_conn:
        print("Dropping 'predatory_journals' table from ria.db...")
        ria_conn.execute(text("DROP TABLE predatory_journals"))
        ria_conn.commit()
        print("Table dropped successfully.")

if __name__ == "__main__":
    migrate_predatory_data()
