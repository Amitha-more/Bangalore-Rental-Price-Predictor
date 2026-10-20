from pathlib import Path
import pandas as pd


# ==================================================
# 1. FILE LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "house_rent_raw.csv"

OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "rentals_clean.csv"


# ==================================================
# 2. LOAD RAW DATA
# ==================================================

df = pd.read_csv(RAW_FILE)

print("Original number of rows:", len(df))


# ==================================================
# 3. CLEAN COLUMN NAMES
# ==================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\nCleaned column names:")
print(df.columns.tolist())


# ==================================================
# 4. CLEAN TEXT COLUMNS
# ==================================================

text_columns = df.select_dtypes(include="str").columns

for column in text_columns:
    df[column] = df[column].str.strip()


# ==================================================
# 5. CONVERT DATE
# ==================================================

df["posted_on"] = pd.to_datetime(
    df["posted_on"],
    errors="coerce"
)


# ==================================================
# 6. STANDARDIZE FURNISHING STATUS
# ==================================================

df["furnishing_status"] = (
    df["furnishing_status"]
    .str.strip()
    .str.title()
)


# ==================================================
# 7. STANDARDIZE CITY
# ==================================================

df["city"] = (
    df["city"]
    .str.strip()
    .str.title()
)


# ==================================================
# 8. CHECK DUPLICATES
# ==================================================

duplicates_before = df.duplicated().sum()

print("\nDuplicate rows found:", duplicates_before)

df = df.drop_duplicates()


# ==================================================
# 9. KEEP ONLY BANGALORE
# ==================================================

df = df[
    df["city"] == "Bangalore"
].copy()

print("\nRows after keeping Bangalore:", len(df))


# ==================================================
# 10. CLEAN LOCALITY TEXT
# ==================================================

df["area_locality"] = (
    df["area_locality"]
    .str.strip()
)


# ==================================================
# 11. CREATE A STANDARD LOCALITY COLUMN
# ==================================================

def standardize_locality(locality):

    locality_lower = locality.lower().strip()

    # ------------------------------
    # Whitefield
    # ------------------------------
    if "whitefield" in locality_lower:
        return "Whitefield"

    # ------------------------------
    # Koramangala
    # ------------------------------
    if "koramangala" in locality_lower:
        return "Koramangala"

    # ------------------------------
    # HSR Layout
    # ------------------------------
    if "hsr layout" in locality_lower:
        return "HSR Layout"

    # ------------------------------
    # Indiranagar
    # ------------------------------
    if locality_lower == "indira nagar":
        return "Indiranagar"

    if "indiranagar" in locality_lower:
        return "Indiranagar"

    # ------------------------------
    # Electronic City
    # ------------------------------
    if "electronic city" in locality_lower:
        return "Electronic City"

    if "electronics city" in locality_lower:
        return "Electronic City"

    # ------------------------------
    # Marathahalli
    # ------------------------------
    if "marathahalli" in locality_lower:
        return "Marathahalli"

    # ------------------------------
    # Everything else
    # ------------------------------
    return None


df["standard_locality"] = (
    df["area_locality"]
    .apply(standardize_locality)
)


# ==================================================
# 12. KEEP OUR SIX PROJECT LOCALITIES
# ==================================================

target_localities = [
    "Whitefield",
    "Koramangala",
    "HSR Layout",
    "Indiranagar",
    "Electronic City",
    "Marathahalli",
]

df = df[
    df["standard_locality"].isin(target_localities)
].copy()


print(
    "\nRows after keeping target localities:",
    len(df)
)


# ==================================================
# 13. REMOVE INVALID NUMERIC VALUES
# ==================================================

df = df[
    (df["rent"] > 0) &
    (df["size"] > 0) &
    (df["bhk"] > 0) &
    (df["bathroom"] > 0)
].copy()


# ==================================================
# 14. CREATE PRICE PER SQFT
# ==================================================

df["rent_per_sqft"] = (
    df["rent"] / df["size"]
)

# ==================================================
# 14A. REMOVE EXTREME DATA-QUALITY OUTLIER
# ==================================================

suspicious_outlier = (
    (df["rent"] > 500000) &
    (df["rent_per_sqft"] > 500)
)

removed_outliers = df[suspicious_outlier].copy()


# Save removed records separately for documentation
OUTLIER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "removed_outliers.csv"
)

if len(removed_outliers) > 0:

    removed_outliers.to_csv(
        OUTLIER_FILE,
        index=False
    )

    print(
        "\nExtreme data-quality outliers removed:",
        len(removed_outliers)
    )

    print(
        removed_outliers[
            [
                "standard_locality",
                "bhk",
                "rent",
                "size",
                "bathroom",
                "rent_per_sqft",
            ]
        ].to_string(index=False)
    )


df = df[~suspicious_outlier].copy()


# ==================================================
# 15. CREATE BHK TO BATHROOM RATIO
# ==================================================

df["bhk_bathroom_ratio"] = (
    df["bhk"] / df["bathroom"]
)


# ==================================================
# 16. SHOW FINAL INFORMATION
# ==================================================

print("\n========== FINAL DATA ==========")

print("Rows:", len(df))

print("\nLocality counts:")

print(
    df["standard_locality"]
    .value_counts()
)


print("\nMissing values:")

print(
    df.isna().sum()
)


print("\nFirst 5 cleaned rows:")

print(
    df.head()
)


# ==================================================
# 17. SAVE CLEAN DATASET
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\nClean dataset saved to:")

print(OUTPUT_FILE)