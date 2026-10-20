import pandas as pd


# --------------------------------------------------
# 1. Load current standardized live data
# --------------------------------------------------

input_file = (
    "data/processed/"
    "all_live_clean_standardized.csv"
)

df = pd.read_csv(input_file)


# --------------------------------------------------
# 2. Find suspiciously low rents
# --------------------------------------------------

suspicious = df[
    df["rent"] < 5000
].copy()


# --------------------------------------------------
# 3. Show suspicious records
# --------------------------------------------------

print("Suspicious rent records:", len(suspicious))

if len(suspicious) > 0:

    print("\nRecords with rent below ₹5,000:")

    print(
        suspicious[
            [
                "listing_id",
                "search_locality",
                "target_locality",
                "bhk",
                "size_sqft",
                "rent",
                "furnishing_status",
                "locality",
                "source_file",
            ]
        ].to_string(index=False)
    )

else:

    print("No suspicious rent records found.")