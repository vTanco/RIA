import requests
import re
from backend.database.session import SessionLocal
from backend.database.models import PredatoryJournal

README_URL = "https://raw.githubusercontent.com/twincacca/PredatoryJournals/main/README.md"

def enrich_data():
    db = SessionLocal()
    print(f"Fetching data from {README_URL}...")
    r = requests.get(README_URL)
    r.raise_for_status()
    
    content = r.text
    lines = content.split('\n')
    
    # Regex to find ISSN: (ISSN: XXXX-XXXX) or similar
    issn_pattern = re.compile(r'\(ISSN:\s*([\dX-]{8,9})\)', re.IGNORECASE)
    
    count = 0
    new_records = 0
    
    for line in lines:
        line = line.strip()
        if not line.startswith('- '):
            continue
            
        # Extract name: usually "- Name [email]" or "- Name (ISSN) [email]"
        # Let's try to split by '[' first to get the part before email
        parts = line.split('[')
        name_part = parts[0].replace('- ', '').strip()
        
        # Check for ISSN in name_part
        issn_match = issn_pattern.search(name_part)
        issn = None
        if issn_match:
            issn = issn_match.group(1)
            # Remove ISSN from name
            name_part = issn_pattern.sub('', name_part).strip()
        
        # Clean up name (remove trailing parens if empty)
        name = name_part.strip(' ()')
        
        if not name:
            continue

        # Check if exists
        exists = db.query(PredatoryJournal).filter(PredatoryJournal.name.ilike(f"%{name}%")).first()
        
        if exists:
            if issn and not exists.issn:
                print(f"Updating {name} with ISSN {issn}")
                exists.issn = issn
                count += 1
        else:
            # Add new record if it has ISSN or just to add more data?
            # User wants to fix missing fields. Adding more data is good.
            # But let's prioritize ISSNs.
            if issn:
                print(f"Adding new record {name} with ISSN {issn}")
                journal = PredatoryJournal(
                    name=name,
                    issn=issn,
                    source="Twincacca List",
                    publisher=None
                )
                db.add(journal)
                new_records += 1

    db.commit()
    print(f"Updated {count} records with ISSNs.")
    print(f"Added {new_records} new records.")
    db.close()

if __name__ == "__main__":
    enrich_data()
