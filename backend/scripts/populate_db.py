import pandas as pd
import sys
import os
import argparse
from sqlalchemy.orm import Session

# Add the project root to the python path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.database.session import SessionLocal
from backend.database.models import PredatoryJournal

def populate_db(file_path: str):
    """
    Reads the Excel file and populates the PredatoryJournal table.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"Reading data from {file_path}...")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Check required columns
    required_columns = ["name", "type", "url", "issn_online", "issn_print"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Missing column '{col}' in Excel file.")
            return

    db: Session = SessionLocal()
    
    count_new = 0
    count_updated = 0
    count_skipped = 0

    print("Starting import...")
    
    for index, row in df.iterrows():
        name = str(row["name"]).strip()
        entity_type = str(row["type"]).strip().lower() # journal or publisher
        url = row["url"] if pd.notna(row["url"]) else None
        
        # Combine ISSNs
        issns = []
        if pd.notna(row["issn_online"]):
            issns.append(str(row["issn_online"]))
        if pd.notna(row["issn_print"]):
            issns.append(str(row["issn_print"]))
        
        issn_str = ", ".join(issns) if issns else None

        # Check if exists
        existing = db.query(PredatoryJournal).filter(PredatoryJournal.name == name).first()
        
        if existing:
            # Update if we have new info (optional, but good practice)
            updated = False
            if not existing.url and url:
                existing.url = url
                updated = True
            if not existing.issn and issn_str:
                existing.issn = issn_str
                updated = True
            
            if updated:
                count_updated += 1
            else:
                count_skipped += 1
        else:
            # Create new
            new_entry = PredatoryJournal(
                name=name,
                issn=issn_str,
                publisher=None, # We don't have this explicitly in the current scrape structure for journals, or it is the name for publishers
                source="scraped_list_2025",
                entity_type=entity_type,
                url=url
            )
            db.add(new_entry)
            count_new += 1

        if index % 100 == 0:
            print(f"Processed {index} records...")

    try:
        db.commit()
        print("\n🎉 Import completed successfully!")
        print(f"Added: {count_new}")
        print(f"Updated: {count_updated}")
        print(f"Skipped: {count_skipped}")
    except Exception as e:
        db.rollback()
        print(f"Error committing to database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate database from scraped Excel file.")
    parser.add_argument("--file", type=str, default="full_database_with_issn.xlsx", help="Path to the Excel file")
    args = parser.parse_args()

    populate_db(args.file)
