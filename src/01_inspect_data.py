"""
Stage 1: inspect the raw rental dataset.

Run this file only after placing the CSV in data/raw/.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "house_rent_raw.csv"


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {RAW_FILE}. Put your downloaded CSV there first."
        )

    df = pd.read_csv(RAW_FILE)

    print("\n--- SHAPE ---")
    print(df.shape)

    print("\n--- COLUMN NAMES ---")
    print(df.columns.tolist())

    print("\n--- FIRST 5 ROWS ---")
    print(df.head())

    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    print("\n--- MISSING VALUES ---")
    print(df.isna().sum())

    print("\n--- DUPLICATE ROWS ---")
    print(df.duplicated().sum())


if __name__ == "__main__":
    main()
