import re
from typing import List, Dict

class EvidenceExtractor:
    def __init__(self, text: str):
        self.text = text
        self.lower_text = text.lower()

    def extract_funding(self) -> List[str]:
        patterns = [
            r"funding[:\s]+(.*?)(?:\.|$)",
            r"supported by[:\s]+(.*?)(?:\.|$)",
            r"grant[:\s]+(.*?)(?:\.|$)",
            r"financial support[:\s]+(.*?)(?:\.|$)",
            r"funded by[:\s]+(.*?)(?:\.|$)",
            r"funding provided by[:\s]+(.*?)(?:\.|$)"
        ]
        evidence = []
        for p in patterns:
            matches = re.findall(p, self.text, re.IGNORECASE | re.MULTILINE)
            evidence.extend(matches)
        return list(set(evidence))

    def extract_coi_statement(self) -> List[str]:
        patterns = [
            r"conflict of interest[:\s]+(.*?)(?:\.|$)",
            r"competing interest[:\s]+(.*?)(?:\.|$)",
            r"disclosure[:\s]+(.*?)(?:\.|$)",
            r"declaration of interest[:\s]+(.*?)(?:\.|$)",
            r"authors declare[:\s]+(.*?)(?:\.|$)",
            r"no conflict of interest declared",
            r"no competing interests declared"
        ]
        evidence = []
        for p in patterns:
            matches = re.findall(p, self.text, re.IGNORECASE | re.MULTILINE)
            evidence.extend(matches)
        return list(set(evidence))

    def extract_affiliations(self) -> List[str]:
        # Heuristic: Look for email addresses or "Department of"
        # This is a simplified version.
        patterns = [
            r"((?:Department|Institute|University|Hospital) of [^\n\.]+)",
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        ]
        evidence = []
        for p in patterns:
            matches = re.findall(p, self.text, re.IGNORECASE)
            evidence.extend(matches)
        return list(set(evidence))[:10] # Limit to top 10 to avoid noise

    def check_keywords(self, keywords: List[str]) -> List[str]:
        found = []
        for kw in keywords:
            if kw.lower() in self.lower_text:
                found.append(kw)
        return found
