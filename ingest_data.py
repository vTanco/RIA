import requests
import csv
import io
from backend.database.session import SessionLocal
from backend.database.models import PredatoryJournal

JOURNALS_URL = "https://raw.githubusercontent.com/stop-predatory-journals/stop-predatory-journals.github.io/master/_data/journals.csv"
PUBLISHERS_URL = "https://raw.githubusercontent.com/stop-predatory-journals/stop-predatory-journals.github.io/master/_data/publishers.csv"

def ingest_data():
    db = SessionLocal()
    
    # Clear existing data? Or upsert? User asked to "extract 100% and store", implying a fresh or full load.
    # Let's clear to avoid duplicates if re-running, or we could check existence.
    # Given the user said "database only has 5 records", clearing seems safe to ensure full sync.
    print("Clearing existing records...")
    db.query(PredatoryJournal).delete()
    db.commit()

    count = 0

    # Ingest Journals
    print(f"Fetching journals from {JOURNALS_URL}...")
    r = requests.get(JOURNALS_URL)
    r.raise_for_status()
    
    # The CSV format in that repo usually has columns like: url, title, abbr, issn, etc.
    # Let's parse it.
    f = io.StringIO(r.text)
    reader = csv.DictReader(f)
    
    for row in reader:
        # Map fields
        # Header is: url,name,abbr
        name = row.get('name', '').strip()
        url = row.get('url', '').strip()
        # The GitHub CSV does not have an 'issn' column unfortunately.
        # We will try to extract it if present in other columns or leave it empty.
        issn = None 
        
        if name:
            journal = PredatoryJournal(
                name=name,
                url=url,
                issn=issn,
                source="Stop Predatory Journals (Journals)",
                entity_type="journal",
                publisher=None
            )
            db.add(journal)
            count += 1

    # Ingest Publishers
    print(f"Fetching publishers from {PUBLISHERS_URL}...")
    r = requests.get(PUBLISHERS_URL)
    r.raise_for_status()
    
    f = io.StringIO(r.text)
    reader = csv.DictReader(f)
    
    for row in reader:
        name = row.get('name', '').strip()
        url = row.get('url', '').strip()
        
        if name:
            journal = PredatoryJournal(
                name=name,
                url=url,
                source="Stop Predatory Journals (Publishers)",
                entity_type="publisher",
                publisher=name 
            )
            db.add(journal)
            count += 1

    db.commit()
    print(f"Successfully ingested {count} records.")
    db.close()

if __name__ == "__main__":
    ingest_data()
