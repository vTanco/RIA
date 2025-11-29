from sqlalchemy.orm import Session
from backend.database.models import PredatoryJournal
from typing import Dict, Any, Optional
import re

class PredatoryJournalDetector:
    def __init__(self, db: Session):
        self.db = db

    def detect(self, metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        Detects if the journal is predatory based on metadata.
        Returns a dictionary with flags and details.
        """
        result = {
            "predatory_flag": False,
            "match_type": "None",
            "sources": [],
            "confidence": 0.0,
            "details": ""
        }

        issn = metadata.get("issn")
        journal_name = metadata.get("journal")
        publisher = metadata.get("publisher")

        # Priority 1: ISSN Match
        if issn:
            match = self._match_issn(issn)
            if match:
                result["predatory_flag"] = True
                result["match_type"] = "ISSN"
                result["sources"].append(match.source)
                result["confidence"] = 1.0
                result["details"] = f"Matched ISSN: {issn} in {match.source}"
                return result

        # Priority 2: Journal Name Match
        if journal_name:
            match = self._match_name(journal_name)
            if match:
                result["predatory_flag"] = True
                result["match_type"] = "Name"
                result["sources"].append(match.source)
                result["confidence"] = 0.9 # High confidence for name match
                result["details"] = f"Matched Journal Name: {journal_name} in {match.source}"
                return result

        # Priority 3: Publisher Match
        if publisher:
            match = self._match_publisher(publisher)
            if match:
                result["predatory_flag"] = True
                result["match_type"] = "Publisher"
                result["sources"].append(match.source)
                result["confidence"] = 0.8
                result["details"] = f"Matched Publisher: {publisher} in {match.source}"
                return result

        return result

    def _match_issn(self, issn: str) -> Optional[PredatoryJournal]:
        # Normalize ISSN (remove hyphens for comparison if needed, but usually stored with hyphens)
        return self.db.query(PredatoryJournal).filter(PredatoryJournal.issn == issn).first()

    def _match_name(self, name: str) -> Optional[PredatoryJournal]:
        # Normalize name: lowercase, remove punctuation
        normalized_name = self._normalize_string(name)
        
        # Exact match on normalized name (simplified for performance)
        # In a real production system, we might use fuzzy matching or full-text search
        # Here we rely on the DB having clean names or doing a ILIKE
        
        # Try exact match first
        match = self.db.query(PredatoryJournal).filter(PredatoryJournal.name == name).first()
        if match:
            return match
            
        # Try case-insensitive match
        match = self.db.query(PredatoryJournal).filter(PredatoryJournal.name.ilike(name)).first()
        return match

    def _match_publisher(self, publisher: str) -> Optional[PredatoryJournal]:
        # Check if publisher is in the list (usually we store publishers with a flag or separate table, 
        # but here we assume they are in the same table with a 'publisher' type or just by name)
        # For this implementation, we check if the publisher name exists in the DB as a 'publisher' entry
        # Or if we have a specific 'publisher' column in our PredatoryJournal table that matches.
        
        # Assuming the PredatoryJournal table contains both Journals and Publishers (where name is the publisher name)
        # We can check if the extracted publisher matches any entry known as a publisher.
        
        match = self.db.query(PredatoryJournal).filter(PredatoryJournal.name.ilike(publisher)).first()
        return match

    def _normalize_string(self, s: str) -> str:
        if not s:
            return ""
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s)
        return s.strip()
