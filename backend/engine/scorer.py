from backend.engine.extractors import EvidenceExtractor
from typing import Dict, Any, List

class COIScorer:
    def __init__(self, text: str):
        self.extractor = EvidenceExtractor(text)
        self.evidence = {}
        self.rules_triggered = []

    def compute_score(self) -> Dict[str, Any]:
        # Extract evidence
        funding = self.extractor.extract_funding()
        coi_statements = self.extractor.extract_coi_statement()
        affiliations = self.extractor.extract_affiliations()
        
        self.evidence = {
            "funding": funding,
            "coi_statements": coi_statements,
            "affiliations": affiliations
        }

        # Calculate Dimension Scores
        d1 = self._score_d1_transparency(funding, coi_statements)
        d2 = self._score_d2_funding_alignment(funding)
        d3 = self._score_d3_network(affiliations)
        d4 = self._score_d4_journal() # Placeholder
        d5 = self._score_d5_bias() # Placeholder

        # Overall Score
        overall_score = int((d1 + d2 + d3 + d4 + d5) / 5)
        
        risk_level = "low"
        if overall_score >= 67:
            risk_level = "high"
        elif overall_score >= 34:
            risk_level = "medium"

        return {
            "score": overall_score,
            "overall_risk": risk_level,
            "categories": [
                {"name": "Disclosure & Transparency", "score": d1},
                {"name": "Funding-Outcome Alignment", "score": d2},
                {"name": "Author-Institution Network", "score": d3},
                {"name": "Journal Integrity", "score": d4},
                {"name": "Textual Bias", "score": d5}
            ],
            "evidence": self.evidence,
            "rules_triggered": self.rules_triggered
        }

    def _score_d1_transparency(self, funding: List[str], coi: List[str]) -> int:
        score = 0
        if not coi:
            score += 100
            self.rules_triggered.append("Missing COI statement")
        elif any("declared" in c.lower() or "none" in c.lower() for c in coi):
            score += 0
        else:
            score += 20 # Present but maybe complex
            
        if not funding:
            score += 50
            self.rules_triggered.append("Missing funding statement")
        
        return min(score, 100)

    def _score_d2_funding_alignment(self, funding: List[str]) -> int:
        score = 0
        commercial_keywords = ["pharma", "inc", "ltd", "corp", "company", "laboratories"]
        
        found_commercial = []
        for f in funding:
            for kw in commercial_keywords:
                if kw in f.lower():
                    found_commercial.append(kw)
        
        if found_commercial:
            score += 80
            self.rules_triggered.append(f"Commercial funding detected: {', '.join(set(found_commercial))}")
        
        return min(score, 100)

    def _score_d3_network(self, affiliations: List[str]) -> int:
        score = 0
        commercial_keywords = ["pharma", "inc", "ltd", "corp", "company"]
        
        for aff in affiliations:
            if any(kw in aff.lower() for kw in commercial_keywords):
                score += 60
                self.rules_triggered.append(f"Commercial affiliation: {aff}")
                break # Count once for now
        
        return min(score, 100)

    def _score_d4_journal(self) -> int:
        # Placeholder: In a real app, check against DOAJ/Scopus API
        # For now, return a neutral low risk
        return 10

    def _score_d5_bias(self) -> int:
        # Placeholder: Check for promotional language
        promotional = ["groundbreaking", "miracle", "unprecedented", "perfect"]
        found = self.extractor.check_keywords(promotional)
        if found:
            self.rules_triggered.append(f"Promotional language used: {', '.join(found)}")
            return 40
        return 0
