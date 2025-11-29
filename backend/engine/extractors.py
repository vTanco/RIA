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

class MetadataExtractor:
    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')

    def extract_metadata(self) -> Dict[str, str]:
        return {
            "title": self._extract_title(),
            "journal": self._extract_journal(),
            "issn": self._extract_issn(),
            "doi": self._extract_doi(),
            "publisher": self._extract_publisher(),
            "authors": self._extract_authors(),
            "year": self._extract_year()
        }

    def _extract_authors(self) -> str:
        # Heuristic: Look for lines that look like lists of names near the top
        # This is difficult without NER, but we can try simple heuristics
        # e.g., "By [Name], [Name]" or just lines with comma separated capitalized words
        
        # Very simple placeholder for now
        for line in self.lines[:10]:
            if "By " in line:
                return line.replace("By ", "").strip()
        return "Unknown Authors"

    def _extract_year(self) -> str:
        # Look for 4 digit years in the first page
        matches = re.findall(r"(20[0-2][0-9]|19[0-9]{2})", self.text[:2000])
        if matches:
            # Return the most recent year found, assuming it's the pub year
            return max(matches)
        return "2024"

    def _extract_title(self) -> str:
        # Heuristic: First non-empty line that isn't a header/page number
        # This is very basic and could be improved with layout analysis
        for line in self.lines[:5]:
            if len(line.strip()) > 10:
                return line.strip()
        return "Unknown Title"

    def _extract_issn(self) -> str:
        # Regex for ISSN (XXXX-XXXX)
        pattern = r"ISSN[:\s]+([0-9]{4}-[0-9]{3}[0-9X])"
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Fallback: just look for the pattern without "ISSN" prefix
        pattern_loose = r"([0-9]{4}-[0-9]{3}[0-9X])"
        matches = re.findall(pattern_loose, self.text)
        # Filter out common false positives like years (2020-2021) or pages
        for m in matches:
            if not m.startswith('19') and not m.startswith('20'): # Rough heuristic
                return m
        return None

    def _extract_doi(self) -> str:
        pattern = r"(10\.[0-9]{4,}/[-._;()/:a-zA-Z0-9]+)"
        match = re.search(pattern, self.text)
        if match:
            return match.group(1)
        return None

    def _extract_journal(self) -> str:
        # Very hard to extract reliably without layout.
        # Heuristic: Look for lines containing "Journal of", "Transactions on", etc.
        keywords = ["Journal of", "Transactions on", "Proceedings of", "Review", "Annals"]
        for line in self.lines[:20]: # Check header area
            for kw in keywords:
                if kw in line:
                    return line.strip()
        return None

    def _extract_publisher(self) -> str:
        # Look for known publisher names
        publishers = ["Elsevier", "Springer", "Wiley", "Taylor & Francis", "Sage", "MDPI", "Frontiers", "Hindawi", "IEEE", "ACM"]
        for pub in publishers:
            if pub.lower() in self.text.lower():
                return pub
        return None
