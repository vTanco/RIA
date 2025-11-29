from sqlalchemy.orm import Session
from backend.database.models import PredatoryJournal
import requests
import csv
import io

class PredatoryJournalUpdater:
    def __init__(self, db: Session):
        self.db = db

    def update_database(self):
        """
        Updates the predatory journals database from configured sources.
        """
        print("Starting predatory journal list update...")
        count = 0
        
        # 1. Beall's List (Sample/Static for now as scraping requires more logic)
        # We'll add some known examples for testing
        count += self._add_manual_entries()
        
        # 2. Future: Implement scraping for Beall's list and PredatoryJournals.org
        # count += self._scrape_bealls_list()
        
        print(f"Update complete. Added/Updated {count} entries.")
        return count

    def _add_manual_entries(self) -> int:
        # Sample data for verification
        entries = [
            {"name": "Omics International", "publisher": "Omics", "source": "beall", "url": "https://www.omicsonline.org/"},
            {"name": "Waset", "publisher": "Waset", "source": "beall", "url": "https://waset.org/"},
            {"name": "Science Domain International", "publisher": "Science Domain", "source": "beall", "url": ""},
            {"name": "IOSR Journals", "publisher": "IOSR", "source": "beall", "url": ""},
            {"name": "Fake Predatory Journal", "issn": "1234-5678", "source": "test", "url": "http://fake.com"}
        ]
        
        added = 0
        for entry in entries:
            if self._add_or_update(entry):
                added += 1
        return added

    def _add_or_update(self, data: dict) -> bool:
        # Check if exists by name or ISSN
        existing = None
        if data.get("issn"):
            existing = self.db.query(PredatoryJournal).filter(PredatoryJournal.issn == data["issn"]).first()
        
        if not existing and data.get("name"):
            existing = self.db.query(PredatoryJournal).filter(PredatoryJournal.name == data["name"]).first()
            
        if existing:
            # Update fields if needed
            existing.source = data["source"]
            existing.url = data.get("url")
            existing.publisher = data.get("publisher")
            # self.db.commit() # Commit batch or single?
            return False
        else:
            new_entry = PredatoryJournal(
                name=data.get("name"),
                issn=data.get("issn"),
                publisher=data.get("publisher"),
                source=data["source"],
                url=data.get("url")
            )
            self.db.add(new_entry)
            self.db.commit()
            return True
