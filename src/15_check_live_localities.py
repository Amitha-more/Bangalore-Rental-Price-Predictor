import pandas as pd


# --------------------------------------------------
# 1. Load combined live data
# --------------------------------------------------

input_file = (
    "data/processed/"
    "all_2bhk_live_clean.csv"
)

df = pd.read_csv(input_file)


# --------------------------------------------------
# 2. Show searched locality vs actual locality
# --------------------------------------------------

print("\n========================================")
print("SEARCHED LOCALITY vs ACTUAL LOCALITY")
print("========================================")

for search_locality in sorted(
    df["search_locality"].unique()
):

    print(
        f"\n--- {search_locality} ---"
    )

    subset = df[
        df["search_locality"]
        == search_locality
    ]

    print(
        subset["locality"]
        .value_counts()
        .to_string()
    )


# --------------------------------------------------
# 3. Count unique actual localities
# --------------------------------------------------

print("\n========================================")
print("TOTAL UNIQUE ACTUAL LOCALITIES")
print("========================================")

print(
    df["locality"]
    .value_counts()
    .head(30)
)