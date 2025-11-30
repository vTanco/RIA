from backend.engine.extractors import EvidenceExtractor, MetadataExtractor
from backend.engine.predatory_detector import PredatoryJournalDetector
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple

class COIScorer:
    def __init__(self, text: str, db: Session = None, predatory_db: Session = None):
        self.extractor = EvidenceExtractor(text)
        self.metadata_extractor = MetadataExtractor(text)
        self.db = db
        self.predatory_db = predatory_db
        self.evidence = {}
        self.rules_triggered = []
        self.metadata = {}

    def compute_score(self) -> Dict[str, Any]:
        # Extract evidence
        funding = self.extractor.extract_funding()
        coi_statements = self.extractor.extract_coi_statement()
        affiliations = self.extractor.extract_affiliations()
        
        # Extract Metadata
        self.metadata = self.metadata_extractor.extract_metadata()
        
        self.evidence = {
            "funding": funding,
            "coi_statements": coi_statements,
            "affiliations": affiliations,
            "metadata": self.metadata
        }

        # Calculate Dimension Scores
        s1, e1, r1 = self._score_d1_transparency(funding, coi_statements)
        s2, e2, r2 = self._score_d2_funding_alignment(funding)
        s3, e3, r3 = self._score_d3_network(affiliations)
        s4, e4, r4 = self._score_d4_journal() 
        s5, e5, r5 = self._score_d5_bias() 

        # Overall Score
        overall_score = int((s1 + s2 + s3 + s4 + s5) / 5)
        
        # Override if Predatory Journal
        if self.evidence.get("predatory_check", {}).get("predatory_flag"):
            overall_score = max(overall_score, 100) # Force max risk
            self.rules_triggered.append("CRITICAL: Predatory Journal Detected. Risk set to High.")

        risk_level = self._get_risk_level(overall_score)

        return {
            "score": overall_score,
            "overall_risk": risk_level,
            "categories": [
                {
                    "name": "Disclosure & Funding Transparency",
                    "score": s1,
                    "risk_level": self._get_risk_level(s1),
                    "evidence_found": e1,
                    "rules_applied": r1
                },
                {
                    "name": "Funding-Outcome Alignment",
                    "score": s2,
                    "risk_level": self._get_risk_level(s2),
                    "evidence_found": e2,
                    "rules_applied": r2
                },
                {
                    "name": "Author-Institution-Sponsor Network",
                    "score": s3,
                    "risk_level": self._get_risk_level(s3),
                    "evidence_found": e3,
                    "rules_applied": r3
                },
                {
                    "name": "Journal / Editorial Integrity",
                    "score": s4,
                    "risk_level": self._get_risk_level(s4),
                    "evidence_found": e4,
                    "rules_applied": r4
                },
                {
                    "name": "Textual Bias & Reporting Quality",
                    "score": s5,
                    "risk_level": self._get_risk_level(s5),
                    "evidence_found": e5,
                    "rules_applied": r5
                }
            ],
            "evidence": self.evidence,
            "rules_triggered": self.rules_triggered
        }

    def _get_risk_level(self, score: int) -> str:
        if score >= 67:
            return "high"
        elif score >= 34:
            return "medium"
        return "low"

    def _score_d1_transparency(self, funding: List[str], coi: List[str]) -> Tuple[int, List[str], List[str]]:
        score = 0
        evidence = []
        rules = []

        if not coi:
            score += 100
            evidence.append("No dedicated COI statement mentioned in the paper.")
            rules.append("NO COI section found -> High Risk")
        elif any("declared" in c.lower() or "none" in c.lower() for c in coi):
            score += 0
            evidence.append("COI statement declares no conflicts.")
            rules.append("Explicit 'No Conflict' declaration -> Low Risk")
        else:
            score += 20 
            evidence.append(f"COI statement present: {coi[0][:50]}...")
            rules.append("COI statement present but complex -> Low/Medium Risk")
            
        if not funding:
            score += 50
            evidence.append("No funding statement found.")
            rules.append("Missing funding statement -> Medium Risk")
        else:
            evidence.append(f"Funding found: {funding[0][:50]}...")
        
        return min(score, 100), evidence, rules

    def _score_d2_funding_alignment(self, funding: List[str]) -> Tuple[int, List[str], List[str]]:
        score = 0
        evidence = []
        rules = []
        commercial_keywords = ["pharma", "inc", "ltd", "corp", "company", "laboratories"]
        
        found_commercial = []
        for f in funding:
            for kw in commercial_keywords:
                if kw in f.lower():
                    found_commercial.append(kw)
        
        if found_commercial:
            score += 80
            evidence.append(f"Funding source contains commercial keywords: {', '.join(set(found_commercial))}")
            rules.append("Commercial funding detected -> High Risk")
        elif funding:
            evidence.append("Funding appears to be from non-commercial/public sources.")
            rules.append("Public/Academic funding -> Low Risk")
        else:
            evidence.append("No funding information to analyze for alignment.")
        
        return min(score, 100), evidence, rules

    def _score_d3_network(self, affiliations: List[str]) -> Tuple[int, List[str], List[str]]:
        score = 0
        evidence = []
        rules = []
        commercial_keywords = ["pharma", "inc", "ltd", "corp", "company"]
        
        found_commercial = []
        for aff in affiliations:
            if any(kw in aff.lower() for kw in commercial_keywords):
                found_commercial.append(aff)
                score += 60
        
        if found_commercial:
            evidence.append(f"Authors affiliated with commercial entities: {found_commercial[0]}")
            rules.append("Commercial affiliation detected -> Medium/High Risk")
        else:
            evidence.append("Authors appear to have academic/institutional affiliations.")
            rules.append("Diverse academic affiliations -> Low Risk")
            
        return min(score, 100), evidence, rules

    def _score_d4_journal(self) -> Tuple[int, List[str], List[str]]:
        score = 0
        evidence = []
        rules = []
        
        if self.predatory_db:
            detector = PredatoryJournalDetector(self.predatory_db)
            result = detector.detect(self.metadata)
            
            if result["predatory_flag"]:
                score = 100 
                evidence.append(f"Journal flagged as predatory: {result['details']}")
                rules.append("Predatory Journal Detected -> High Risk")
                self.evidence["predatory_check"] = result
            else:
                score = 10 
                evidence.append("Journal not found in predatory database.")
                rules.append("Reputable journal (not in predatory list) -> Low Risk")
                self.evidence["predatory_check"] = result
        else:
            score = 10 
            evidence.append("Predatory check skipped (DB not available).")
            
        return score, evidence, rules

    def _score_d5_bias(self) -> Tuple[int, List[str], List[str]]:
        score = 0
        evidence = []
        rules = []
        
        promotional = ["groundbreaking", "miracle", "unprecedented", "perfect", "amazing"]
        found = self.extractor.check_keywords(promotional)
        
        if found:
            score = 40
            evidence.append(f"Promotional language detected: {', '.join(found)}")
            rules.append("Promotional language usage -> Medium Risk")
        else:
            evidence.append("Language appears sober and scientific.")
            rules.append("No promotional language detected -> Low Risk")
            
        return score, evidence, rules
