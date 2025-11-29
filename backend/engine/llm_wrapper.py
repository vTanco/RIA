from typing import Optional, Dict, Any
import openai

class LLMWrapper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def summarize_risk(self, analysis_result: Dict[str, Any], score: int) -> str:
        """
        Generates a summary of the risk based on the score and extracted evidence using OpenAI.
        """
        if not self.client:
            return self._heuristic_summary(score)
        
        try:
            prompt = f"""
            You are an expert Research Integrity Analyst. Analyze the following conflict-of-interest data extracted from a scientific paper.
            
            Risk Score: {score}/100 (Higher is worse)
            Risk Level: {analysis_result.get('overall_risk', 'unknown')}
            
            Key Evidence Found:
            - Funding: {analysis_result.get('evidence', {}).get('funding', [])}
            - COI Statements: {analysis_result.get('evidence', {}).get('coi_statements', [])}
            - Affiliations: {analysis_result.get('evidence', {}).get('affiliations', [])}
            - Predatory Journal Check: {analysis_result.get('evidence', {}).get('predatory_check', 'Not detected')}
            - Rules Triggered: {analysis_result.get('rules_triggered', [])}
            
            Task:
            Write a concise, professional executive summary (max 3 sentences) explaining why this paper received this score. Focus on the specific evidence found (e.g., commercial funding, missing disclosures). Be objective but firm.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._heuristic_summary(score)

    def _heuristic_summary(self, score: int) -> str:
        if score < 34:
            return "The analysis indicates a LOW risk of conflict of interest. Disclosures appear transparent, and funding sources are likely public or non-commercial."
        elif score < 67:
            return "The analysis indicates a MEDIUM risk. There may be some commercial affiliations or vague funding statements that require further scrutiny."
        else:
            return "The analysis indicates a HIGH risk of conflict of interest. Significant commercial ties, lack of clear disclosures, or potential funding bias detected."
