import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Importing COIScorer...")
    from backend.engine.scorer import COIScorer
    print("COIScorer imported successfully.")
    
    print("Importing PredatoryJournalDetector...")
    from backend.engine.predatory_detector import PredatoryJournalDetector
    print("PredatoryJournalDetector imported successfully.")
    
    print("Importing MetadataExtractor...")
    from backend.engine.extractors import MetadataExtractor
    print("MetadataExtractor imported successfully.")

    print("Importing analysis endpoint...")
    from backend.api.api_v1.endpoints import analysis
    print("Analysis endpoint imported successfully.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
