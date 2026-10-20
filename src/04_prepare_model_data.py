from pathlib import Path

import pandas as pd


# ==================================================
# 1. FILE LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rentals_clean.csv"
)

MODEL_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_data.csv"
)


# ==================================================
# 2. LOAD CLEAN DATA
# ==================================================

df = pd.read_csv(CLEAN_FILE)


print("==================================================")
print("MODEL DATA PREPARATION")
print("==================================================")


print("\nOriginal shape:")

print(df.shape)


# ==================================================
# 3. SELECT MODEL COLUMNS
# ==================================================

model_columns = [
    "standard_locality",
    "size",
    "bhk",
    "bathroom",
    "furnishing_status",
    "bhk_bathroom_ratio",
    "rent",
]


model_df = df[
    model_columns
].copy()


# ==================================================
# 4. RENAME COLUMNS FOR CLARITY
# ==================================================

model_df = model_df.rename(
    columns={
        "standard_locality": "locality",
        "size": "size_sqft",
        "bathroom": "bathrooms",
    }
)


# ==================================================
# 5. CHECK MODEL DATA
# ==================================================

print("\n========== MODEL COLUMNS ==========")

print(
    model_df.columns.tolist()
)


print("\n========== MODEL DATA SHAPE ==========")

print(
    model_df.shape
)


print("\n========== MISSING VALUES ==========")

print(
    model_df.isna().sum()
)


print("\n========== FIRST 5 ROWS ==========")

print(
    model_df.head()
)


print("\n========== DATA TYPES ==========")

print(
    model_df.dtypes
)


# ==================================================
# 6. SAVE MODEL DATA
# ==================================================

MODEL_DATA_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

model_df.to_csv(
    MODEL_DATA_FILE,
    index=False
)


print("\nModel-ready data saved to:")

print(MODEL_DATA_FILE)