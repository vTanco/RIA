import pandas as pd
import os

files = [
    "RESOURCES/The Predatory Journals List 2025.xlsx",
    "RESOURCES/The Predatory Publishers List 2025-2.xlsx"
]

for f in files:
    path = os.path.join("/Users/vicente.tancoedu.uah.es/RIA", f)
    print(f"--- Inspecting {f} ---")
    try:
        df = pd.read_excel(path)
        print("Columns:", df.columns.tolist())
        print("First 2 rows:")
        print(df.head(2))
    except Exception as e:
        print(f"Error reading {f}: {e}")
