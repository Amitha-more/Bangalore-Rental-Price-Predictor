import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

input_file = Path(
    "data/processed/whitefield_2bhk_current_clean.csv"
)

listings_output = Path(
    "data/processed/whitefield_2bhk_comparables.csv"
)

summary_output = Path(
    "data/processed/whitefield_2bhk_market_benchmark.csv"
)


# --------------------------------------------------
# 2. Load cleaned live data
# --------------------------------------------------

df = pd.read_csv(input_file)

print("Input shape:", df.shape)


# --------------------------------------------------
# 3. Keep only exact Whitefield listings
# --------------------------------------------------

df["locality_clean"] = (
    df["locality"]
    .astype(str)
    .str.strip()
    .str.lower()
)

whitefield_df = df[
    df["locality_clean"].isin(
        ["whitefield", "whitefield, bangalore"]
    )
].copy()


# --------------------------------------------------
# 4. Calculate rent per square foot
# --------------------------------------------------

whitefield_df["rent_per_sqft"] = (
    whitefield_df["rent"] / whitefield_df["size_sqft"]
)


# --------------------------------------------------
# 5. Save comparable listings
# --------------------------------------------------

whitefield_df.to_csv(
    listings_output,
    index=False
)


# --------------------------------------------------
# 6. Calculate market benchmark
# --------------------------------------------------

median_rent = whitefield_df["rent"].median()
q1_rent = whitefield_df["rent"].quantile(0.25)
q3_rent = whitefield_df["rent"].quantile(0.75)
mean_rent = whitefield_df["rent"].mean()

median_rent_per_sqft = (
    whitefield_df["rent_per_sqft"].median()
)

benchmark = pd.DataFrame(
    {
        "locality": ["Whitefield"],
        "bhk": [2],
        "listing_count": [len(whitefield_df)],
        "median_rent": [median_rent],
        "q1_rent": [q1_rent],
        "q3_rent": [q3_rent],
        "mean_rent": [mean_rent],
        "median_rent_per_sqft": [median_rent_per_sqft],
    }
)


# --------------------------------------------------
# 7. Save benchmark
# --------------------------------------------------

benchmark.to_csv(
    summary_output,
    index=False
)


# --------------------------------------------------
# 8. Print results
# --------------------------------------------------

print("\nWhitefield comparable listings:", len(whitefield_df))

print("\nCurrent rent summary:")
print(whitefield_df["rent"].describe())

print("\nMedian rent:", round(median_rent))
print("Q1 rent:", round(q1_rent))
print("Q3 rent:", round(q3_rent))

print("\nMedian rent per sqft:",
      round(median_rent_per_sqft, 2))

print("\nSaved comparable listings:")
print(listings_output)

print("\nSaved market benchmark:")
print(summary_output)