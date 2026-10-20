import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

input_file = Path(
    "data/processed/all_2bhk_live_standardized.csv"
)

output_file = Path(
    "data/processed/all_2bhk_market_benchmarks.csv"
)


# --------------------------------------------------
# 2. Load data
# --------------------------------------------------

df = pd.read_csv(input_file)


# --------------------------------------------------
# 3. Remove unavailable listings
# --------------------------------------------------

status_text = (
    df["availabilityStatus"]
    .fillna("")
    .astype(str)
    .str.lower()
)

df = df[
    ~status_text.str.contains(
        "rented|timed out",
        regex=True,
        na=False
    )
].copy()


# --------------------------------------------------
# 4. Calculate rent per sqft
# --------------------------------------------------

df["rent_per_sqft"] = (
    df["rent"] / df["size_sqft"]
)


# --------------------------------------------------
# 5. Target localities
# --------------------------------------------------

localities = [
    "Whitefield",
    "Koramangala",
    "HSR Layout",
    "Indiranagar",
    "Electronic City",
    "Marathahalli",
]


# --------------------------------------------------
# 6. Build benchmarks
# --------------------------------------------------

results = []

for locality in localities:

    subset = df[
        df["target_locality"] == locality
    ].copy()

    if len(subset) == 0:
        results.append(
            {
                "locality": locality,
                "bhk": 2,
                "listing_count": 0,
                "median_rent": None,
                "q1_rent": None,
                "q3_rent": None,
                "median_rent_per_sqft": None,
            }
        )

        continue

    results.append(
        {
            "locality": locality,
            "bhk": 2,
            "listing_count": len(subset),
            "median_rent": subset["rent"].median(),
            "q1_rent": subset["rent"].quantile(0.25),
            "q3_rent": subset["rent"].quantile(0.75),
            "median_rent_per_sqft": (
                subset["rent_per_sqft"].median()
            ),
        }
    )


# --------------------------------------------------
# 7. Create summary table
# --------------------------------------------------

benchmark_df = pd.DataFrame(results)


# --------------------------------------------------
# 8. Save
# --------------------------------------------------

benchmark_df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# 9. Print
# --------------------------------------------------

print("\nCURRENT 2-BHK MARKET BENCHMARKS")
print("================================")

print(
    benchmark_df.to_string(index=False)
)

print("\nSaved to:")
print(output_file)