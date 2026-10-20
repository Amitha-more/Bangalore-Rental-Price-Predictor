import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

input_file = Path("data/live_raw/whitefield_2bhk_current.csv")
output_file = Path("data/processed/whitefield_2bhk_current_clean.csv")


# --------------------------------------------------
# 2. Load live NoBroker data
# --------------------------------------------------

df = pd.read_csv(input_file)

print("Original shape:", df.shape)


# --------------------------------------------------
# 3. Keep only the columns we need
# --------------------------------------------------

live_df = df[
    [
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
    ]
].copy()


# --------------------------------------------------
# 4. Rename columns to simple names
# --------------------------------------------------

live_df = live_df.rename(
    columns={
        "propertyId": "listing_id",
        "propertySize": "size_sqft",
        "furnishing": "furnishing_status",
        "price": "rent",
        "_fetchedAt": "fetched_at",
    }
)


# --------------------------------------------------
# 5. Basic cleaning
# --------------------------------------------------

live_df["locality"] = live_df["locality"].astype(str).str.strip()
live_df["furnishing_status"] = (
    live_df["furnishing_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

live_df["city"] = live_df["city"].astype(str).str.strip().str.title()

live_df["bhk"] = pd.to_numeric(live_df["bhk"], errors="coerce")
live_df["size_sqft"] = pd.to_numeric(live_df["size_sqft"], errors="coerce")
live_df["bathrooms"] = pd.to_numeric(live_df["bathrooms"], errors="coerce")
live_df["rent"] = pd.to_numeric(live_df["rent"], errors="coerce")


# --------------------------------------------------
# 6. Remove invalid rows
# --------------------------------------------------

live_df = live_df.dropna(
    subset=["listing_id", "size_sqft", "bathrooms", "bhk", "rent"]
)

live_df = live_df[
    (live_df["size_sqft"] > 0)
    & (live_df["bathrooms"] > 0)
    & (live_df["bhk"] > 0)
    & (live_df["rent"] > 0)
]


# --------------------------------------------------
# 7. Remove duplicate listings
# --------------------------------------------------

live_df = live_df.drop_duplicates(subset="listing_id")


# --------------------------------------------------
# 8. Save cleaned live data
# --------------------------------------------------

output_file.parent.mkdir(parents=True, exist_ok=True)

live_df.to_csv(output_file, index=False)


# --------------------------------------------------
# 9. Print results
# --------------------------------------------------

print("Cleaned shape:", live_df.shape)

print("\nLocality counts:")
print(live_df["locality"].value_counts())

print("\nBHK counts:")
print(live_df["bhk"].value_counts())

print("\nRent summary:")
print(live_df["rent"].describe())

print("\nSaved to:")
print(output_file)