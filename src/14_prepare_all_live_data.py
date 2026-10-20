import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Folder locations
# --------------------------------------------------

input_folder = Path("data/live_raw")

output_file = Path(
    "data/processed/all_2bhk_live_clean.csv"
)


# --------------------------------------------------
# 2. Find all 2-BHK live CSV files
# --------------------------------------------------

files = sorted(
    input_folder.glob("*_2bhk_current.csv")
)

print("Live files found:", len(files))

for file in files:
    print(" -", file.name)


# --------------------------------------------------
# 3. Check that all 6 files exist
# --------------------------------------------------

if len(files) != 6:
    raise ValueError(
        f"Expected 6 live 2-BHK files, "
        f"but found {len(files)}."
    )


# --------------------------------------------------
# 4. Read and combine files
# --------------------------------------------------

all_data = []

for file in files:

    df = pd.read_csv(file)

    # Remember which search this listing came from
    search_name = file.stem.replace(
        "_current", ""
    )

    df["search_locality"] = search_name

    # Remember original source file
    df["source_file"] = file.name

    all_data.append(df)


combined_df = pd.concat(
    all_data,
    ignore_index=True
)


print(
    "\nCombined original shape:",
    combined_df.shape
)


# --------------------------------------------------
# 5. Keep the columns needed for our project
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
# 6. Rename columns
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
# 7. Clean text columns
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
# 8. Clean furnishing names
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
# 9. Convert numeric columns
# --------------------------------------------------

numeric_columns = [
    "bhk",
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
# 10. Remove invalid records
# --------------------------------------------------

live_df = live_df.dropna(
    subset=[
        "listing_id",
        "bhk",
        "size_sqft",
        "bathrooms",
        "rent",
    ]
)

live_df = live_df[
    (live_df["bhk"] > 0)
    & (live_df["size_sqft"] > 0)
    & (live_df["bathrooms"] > 0)
    & (live_df["rent"] > 0)
]


# --------------------------------------------------
# 11. Remove duplicate listings
# --------------------------------------------------

before_duplicates = len(live_df)

live_df = live_df.drop_duplicates(
    subset="listing_id"
)

duplicates_removed = (
    before_duplicates - len(live_df)
)


# --------------------------------------------------
# 12. Add rent per sqft
# --------------------------------------------------

live_df["rent_per_sqft"] = (
    live_df["rent"]
    / live_df["size_sqft"]
)


# --------------------------------------------------
# 13. Save combined live dataset
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
# 14. Print results
# --------------------------------------------------

print(
    "\nFinal combined shape:",
    live_df.shape
)

print(
    "\nDuplicates removed:",
    duplicates_removed
)

print(
    "\nListings by search locality:"
)

print(
    live_df["search_locality"]
    .value_counts()
)


print(
    "\nBHK counts:"
)

print(
    live_df["bhk"]
    .value_counts()
)


print(
    "\nRent summary:"
)

print(
    live_df["rent"].describe()
)


print(
    "\nSaved to:"
)

print(output_file)