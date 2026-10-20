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
# 2. Example apartment
# --------------------------------------------------

target_locality = "Whitefield"
target_bhk = 2
target_size = 1200


# --------------------------------------------------
# 3. Keep same locality + BHK
# --------------------------------------------------

comparables = df[
    (df["locality_clean"].isin(
        ["whitefield", "whitefield, bangalore"]
    ))
    & (df["bhk"] == target_bhk)
].copy()


# --------------------------------------------------
# 4. Keep listings within ±20% of apartment size
# --------------------------------------------------

lower_size = target_size * 0.80
upper_size = target_size * 1.20

comparables = comparables[
    (comparables["size_sqft"] >= lower_size)
    & (comparables["size_sqft"] <= upper_size)
].copy()


# --------------------------------------------------
# 5. Calculate market statistics
# --------------------------------------------------

median_rent = comparables["rent"].median()
q1_rent = comparables["rent"].quantile(0.25)
q3_rent = comparables["rent"].quantile(0.75)

median_rent_per_sqft = comparables["rent_per_sqft"].median()


# --------------------------------------------------
# 6. Show results
# --------------------------------------------------

print("Target apartment:")
print("Locality:", target_locality)
print("BHK:", target_bhk)
print("Size:", target_size, "sqft")

print("\nComparable listings found:", len(comparables))

print("\nComparable listings:")
print(
    comparables[
        [
            "locality",
            "bhk",
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
print(
    "Median rent per sqft: ₹",
    round(median_rent_per_sqft, 2)
)