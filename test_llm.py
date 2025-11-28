from backend.engine.llm_wrapper import LLMWrapper

def test_llm():
    print("Testing LLM Wrapper...")
    llm = LLMWrapper()
    
    mock_data = {
        "overall_risk": "medium",
        "evidence": {
            "funding": ["Pharma Corp Grant"],
            "coi_statements": ["No conflict declared"],
            "affiliations": ["University of Science"],
        },
        "rules_triggered": ["Commercial funding detected"]
    }
    
    summary = llm.summarize_risk(mock_data, 55)
    print("\nGenerated Summary:")
    print(summary)

if __name__ == "__main__":
    test_llm()
