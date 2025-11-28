from backend.engine.scorer import COIScorer

def test_scorer():
    # Test Case 1: High Risk
    text_high_risk = """
    This study was funded by Pharma Corp Inc. 
    The authors declare no conflict of interest.
    Affiliations: Department of Research, Pharma Corp Inc.
    Results: The drug is a perfect miracle cure.
    """
    scorer = COIScorer(text_high_risk)
    result = scorer.compute_score()
    print("Test Case 1 (High Risk):")
    print(f"Score: {result['score']}")
    print(f"Risk: {result['overall_risk']}")
    print(f"Rules: {result['rules_triggered']}")
    print("-" * 20)

    # Test Case 2: Low Risk
    text_low_risk = """
    This study was supported by the National Institutes of Health.
    The authors declare no competing interests.
    Affiliations: University of Science.
    Results: The results are inconclusive.
    """
    scorer = COIScorer(text_low_risk)
    result = scorer.compute_score()
    print("Test Case 2 (Low Risk):")
    print(f"Score: {result['score']}")
    print(f"Risk: {result['overall_risk']}")
    print(f"Rules: {result['rules_triggered']}")
    print("-" * 20)

if __name__ == "__main__":
    test_scorer()
