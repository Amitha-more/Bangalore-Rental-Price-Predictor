import pandas as pd
from pathlib import Path
import re


# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

input_folder = Path("data/live_raw")

output_file = Path(
    "data/processed/all_live_clean_standardized.csv"
)


# --------------------------------------------------
# 2. Find all live BHK files
# --------------------------------------------------

files = sorted(
    input_folder.glob("*bhk_current.csv")
)

print("Live files found:", len(files))

for file in files:
    print(" -", file.name)


# --------------------------------------------------
# 3. Check expected number of files
# --------------------------------------------------

if len(files) != 24:
    raise ValueError(
        f"Expected 24 live files "
        f"(6 localities × 4 BHK types), "
        f"but found {len(files)}."
    )


# --------------------------------------------------
# 4. Locality names from filenames
# --------------------------------------------------

locality_names = {
    "whitefield": "Whitefield",
    "koramangala": "Koramangala",
    "hsr_layout": "HSR Layout",
    "indiranagar": "Indiranagar",
    "electronic_city": "Electronic City",
    "marathahalli": "Marathahalli",
}


# --------------------------------------------------
# 5. Read every file
# --------------------------------------------------

all_data = []

for file in files:

    # ----------------------------------------------
    # Extract locality + BHK from filename
    # ----------------------------------------------

    match = re.match(
        r"(.+)_(1|2|3|4)bhk_current\.csv$",
        file.name
    )

    if not match:
        raise ValueError(
            f"Unexpected filename format: {file.name}"
        )

    locality_key = match.group(1)
    search_bhk = int(match.group(2))

    if locality_key not in locality_names:
        raise ValueError(
            f"Unknown locality in filename: "
            f"{locality_key}"
        )

    search_locality = locality_names[locality_key]

    # ----------------------------------------------
    # Read CSV
    # ----------------------------------------------

    df = pd.read_csv(file)

    print(
        f"\n{file.name} → {len(df)} rows"
    )

    # ----------------------------------------------
    # Remember search details
    # ----------------------------------------------

    df["search_locality"] = search_locality
    df["search_bhk"] = search_bhk
    df["source_file"] = file.name

    all_data.append(df)


# --------------------------------------------------
# 6. Combine all files
# --------------------------------------------------

combined_df = pd.concat(
    all_data,
    ignore_index=True
)

print(
    "\nCombined original shape:",
    combined_df.shape
)


# --------------------------------------------------
# 7. Required columns
# --------------------------------------------------

required_columns = [
    "propertyId",
    "city",
    "locality",
    "bhk",
    "propertySize",
    "bathrooms",
    "furnishing",
    "price",
    "availabilityStatus",
    "listedOn",
    "_fetchedAt",
    "url",
    "search_locality",
    "search_bhk",
    "source_file",
]


missing_columns = [
    column
    for column in required_columns
    if column not in combined_df.columns
]

if missing_columns:
    raise ValueError(
        "Missing columns: "
        + ", ".join(missing_columns)
    )


live_df = combined_df[
    required_columns
].copy()


# --------------------------------------------------
# 8. Rename columns
# --------------------------------------------------

live_df = live_df.rename(
    columns={
        "propertyId": "listing_id",
        "propertySize": "size_sqft",
        "furnishing": "furnishing_status",
        "price": "rent",
        "listedOn": "listed_on",
        "_fetchedAt": "fetched_at",
    }
)


# --------------------------------------------------
# 9. Clean text columns
# --------------------------------------------------

text_columns = [
    "city",
    "locality",
    "furnishing_status",
    "availabilityStatus",
    "url",
    "search_locality",
    "source_file",
]

for column in text_columns:

    live_df[column] = (
        live_df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# --------------------------------------------------
# 10. Clean furnishing names
# --------------------------------------------------

live_df["furnishing_status"] = (
    live_df["furnishing_status"]
    .replace(
        {
            "Semi": "Semi-Furnished",
            "Full": "Furnished",
            "Unfurnished": "Unfurnished",
        }
    )
)


# --------------------------------------------------
# 11. Convert numeric columns
# --------------------------------------------------

numeric_columns = [
    "bhk",
    "search_bhk",
    "size_sqft",
    "bathrooms",
    "rent",
]

for column in numeric_columns:

    live_df[column] = pd.to_numeric(
        live_df[column],
        errors="coerce"
    )


# --------------------------------------------------
# 12. Remove invalid records
# --------------------------------------------------

before_cleaning = len(live_df)

live_df = live_df.dropna(
    subset=[
        "listing_id",
        "bhk",
        "search_bhk",
        "size_sqft",
        "bathrooms",
        "rent",
    ]
)

live_df = live_df[
    (live_df["bhk"] > 0)
    & (live_df["search_bhk"] > 0)
    & (live_df["size_sqft"] > 0)
    & (live_df["bathrooms"] > 0)
    & (live_df["rent"] > 5000)
]


invalid_removed = (
    before_cleaning - len(live_df)
)


# --------------------------------------------------
# 13. Keep only the requested BHK
# --------------------------------------------------
#
# This is especially important for 4+ searches.
#
# Example:
# 4+ search may return 4, 5 or 6 BHK.
# We keep only actual bhk == 4.
# --------------------------------------------------

before_bhk_filter = len(live_df)

live_df = live_df[
    live_df["bhk"] == live_df["search_bhk"]
].copy()

wrong_bhk_removed = (
    before_bhk_filter - len(live_df)
)


# --------------------------------------------------
# 14. Standardize actual locality
# --------------------------------------------------

live_df["locality_text"] = (
    live_df["locality"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

live_df["target_locality"] = pd.NA


# Whitefield
live_df.loc[
    live_df["locality_text"].str.contains(
        "whitefield",
        regex=False,
        na=False
    ),
    "target_locality"
] = "Whitefield"


# Koramangala
live_df.loc[
    live_df["locality_text"].str.contains(
        "koramangala|kormangala",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Koramangala"


# HSR Layout
live_df.loc[
    live_df["locality_text"].str.contains(
        "hsr layout",
        regex=False,
        na=False
    ),
    "target_locality"
] = "HSR Layout"


# Indiranagar
live_df.loc[
    live_df["locality_text"].str.contains(
        "indiranagar|indira nagar",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Indiranagar"


# Electronic City
live_df.loc[
    live_df["locality_text"].str.contains(
        "electronic city|electronics city",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Electronic City"


# Marathahalli
live_df.loc[
    live_df["locality_text"].str.contains(
        "marathahalli|marthahalli",
        regex=True,
        na=False
    ),
    "target_locality"
] = "Marathahalli"


# --------------------------------------------------
# 15. Remove nearby / unrelated localities
# --------------------------------------------------

before_locality_filter = len(live_df)

live_df = live_df[
    live_df["target_locality"].notna()
].copy()

nearby_removed = (
    before_locality_filter - len(live_df)
)


# --------------------------------------------------
# 16. Remove duplicate property IDs
# --------------------------------------------------

before_duplicates = len(live_df)

live_df = live_df.drop_duplicates(
    subset="listing_id"
)

duplicates_removed = (
    before_duplicates - len(live_df)
)


# --------------------------------------------------
# 17. Calculate rent per sqft
# --------------------------------------------------

live_df["rent_per_sqft"] = (
    live_df["rent"]
    / live_df["size_sqft"]
)


# --------------------------------------------------
# 18. Save final live dataset
# --------------------------------------------------

output_file.parent.mkdir(
    parents=True,
    exist_ok=True
)

live_df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# 19. Print final results
# --------------------------------------------------

print("\n========================================")
print("FINAL LIVE DATASET")
print("========================================")

print(
    "Final shape:",
    live_df.shape
)

print(
    "\nInvalid rows removed:",
    invalid_removed
)

print(
    "Wrong-BHK rows removed:",
    wrong_bhk_removed
)

print(
    "Nearby/other-locality rows removed:",
    nearby_removed
)

print(
    "Duplicate listings removed:",
    duplicates_removed
)


print("\nListings by target locality:")

print(
    live_df["target_locality"]
    .value_counts()
    .sort_index()
)


print("\nListings by BHK:")

print(
    live_df["bhk"]
    .value_counts()
    .sort_index()
)


print(
    "\nLocality × BHK:"
)

print(
    pd.crosstab(
        live_df["target_locality"],
        live_df["bhk"]
    )
)


print("\nRent summary:")

print(
    live_df["rent"].describe()
)


print("\nSaved to:")

print(output_file)