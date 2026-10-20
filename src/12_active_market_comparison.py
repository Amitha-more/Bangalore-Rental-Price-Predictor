import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Load comparable listings
# --------------------------------------------------

input_file = Path(
    "data/processed/whitefield_2bhk_comparables.csv"
)

df = pd.read_csv(input_file)


# --------------------------------------------------
# 2. Target apartment
# --------------------------------------------------

target_bhk = 2
target_size = 1200


# --------------------------------------------------
# 3. Same BHK
# --------------------------------------------------

comparables = df[
    df["bhk"] == target_bhk
].copy()


# --------------------------------------------------
# 4. Similar size: ±20%
# --------------------------------------------------

lower_size = target_size * 0.80
upper_size = target_size * 1.20

comparables = comparables[
    (comparables["size_sqft"] >= lower_size)
    & (comparables["size_sqft"] <= upper_size)
].copy()


# --------------------------------------------------
# 5. Remove explicitly rented / timed-out listings
# --------------------------------------------------

status_text = (
    comparables["availabilityStatus"]
    .fillna("")
    .astype(str)
    .str.lower()
)

comparables = comparables[
    ~status_text.str.contains(
        "rented|timed out",
        na=False
    )
].copy()


# --------------------------------------------------
# 6. Market statistics
# --------------------------------------------------

median_rent = comparables["rent"].median()
q1_rent = comparables["rent"].quantile(0.25)
q3_rent = comparables["rent"].quantile(0.75)


# --------------------------------------------------
# 7. Print results
# --------------------------------------------------

print("Target:")
print("BHK:", target_bhk)
print("Size:", target_size, "sqft")

print(
    "\nActive comparable listings:",
    len(comparables)
)

print("\nComparable listings:")
print(
    comparables[
        [
            "locality",
            "size_sqft",
            "bathrooms",
            "furnishing_status",
            "rent",
            "availabilityStatus",
        ]
    ].to_string(index=False)
)

print("\nCurrent market reference:")
print("Median rent: ₹", round(median_rent))
print("Q1 rent: ₹", round(q1_rent))
print("Q3 rent: ₹", round(q3_rent))