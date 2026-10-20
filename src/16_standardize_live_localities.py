import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

input_file = Path(
    "data/processed/all_2bhk_live_clean.csv"
)

output_file = Path(
    "data/processed/all_2bhk_live_standardized.csv"
)


# --------------------------------------------------
# 2. Load combined live data
# --------------------------------------------------

df = pd.read_csv(input_file)


# --------------------------------------------------
# 3. Clean locality text
# --------------------------------------------------

df["locality_text"] = (
    df["locality"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)


# --------------------------------------------------
# 4. Create standard target locality
# --------------------------------------------------

df["target_locality"] = pd.NA


# Whitefield
df.loc[
    df["locality_text"].str.contains(
        "whitefield",
        regex=False,
        na=False
    ),
    "target_locality"
] = "Whitefield"


# Koramangala
df.loc[
    df["locality_text"].str.contains(
        "koramangala|kormangala",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Koramangala"


# HSR Layout
df.loc[
    df["locality_text"].str.contains(
        "hsr layout",
        regex=False,
        na=False
    ),
    "target_locality"
] = "HSR Layout"


# Indiranagar
df.loc[
    df["locality_text"].str.contains(
        "indiranagar|indira nagar",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Indiranagar"


# Electronic City
df.loc[
    df["locality_text"].str.contains(
        "electronic city|electronics city",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Electronic City"


# Marathahalli
df.loc[
    df["locality_text"].str.contains(
        "marathahalli|marthahalli",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Marathahalli"


# --------------------------------------------------
# 5. Count exact/accepted target localities
# --------------------------------------------------

standardized_df = df[
    df["target_locality"].notna()
].copy()


# --------------------------------------------------
# 6. Print results
# --------------------------------------------------

print("Original rows:", len(df))

print(
    "Rows matching target localities:",
    len(standardized_df)
)

print(
    "Rows excluded as nearby/other localities:",
    len(df) - len(standardized_df)
)


print("\nTarget locality counts:")

print(
    standardized_df["target_locality"]
    .value_counts()
)


print("\nBHK counts:")

print(
    standardized_df["bhk"]
    .value_counts()
)


# --------------------------------------------------
# 7. Save standardized dataset
# --------------------------------------------------

standardized_df.to_csv(
    output_file,
    index=False
)


print("\nSaved to:")
print(output_file)