from pathlib import Path
import pandas as pd


# ==================================================
# 1. FILE LOCATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rentals_clean.csv"
)


# ==================================================
# 2. LOAD CLEAN DATA
# ==================================================

df = pd.read_csv(CLEAN_FILE)


print("==================================================")
print("QUALITY CHECKS")
print("==================================================")


# ==================================================
# 3. BASIC INFORMATION
# ==================================================

print("\n========== DATASET SIZE ==========")

print("Rows:", len(df))

print("Columns:", len(df.columns))


# ==================================================
# 4. NUMERIC SUMMARY
# ==================================================

print("\n========== NUMERIC SUMMARY ==========")

print(
    df[
        [
            "rent",
            "size",
            "bhk",
            "bathroom",
            "rent_per_sqft",
            "bhk_bathroom_ratio",
        ]
    ].describe()
)


# ==================================================
# 5. CHECK MINIMUM VALUES
# ==================================================

print("\n========== MINIMUM VALUES ==========")

print(
    df[
        [
            "rent",
            "size",
            "bhk",
            "bathroom",
            "rent_per_sqft",
            "bhk_bathroom_ratio",
        ]
    ].min()
)


# ==================================================
# 6. CHECK MAXIMUM VALUES
# ==================================================

print("\n========== MAXIMUM VALUES ==========")

print(
    df[
        [
            "rent",
            "size",
            "bhk",
            "bathroom",
            "rent_per_sqft",
            "bhk_bathroom_ratio",
        ]
    ].max()
)


# ==================================================
# 7. RENT BY LOCALITY
# ==================================================

print("\n========== RENT BY LOCALITY ==========")

locality_summary = (
    df
    .groupby("standard_locality")["rent"]
    .agg(
        count="count",
        average="mean",
        minimum="min",
        median="median",
        maximum="max",
    )
    .sort_values("average", ascending=False)
)

print(locality_summary)


# ==================================================
# 8. SIZE BY LOCALITY
# ==================================================

print("\n========== SIZE BY LOCALITY ==========")

size_summary = (
    df
    .groupby("standard_locality")["size"]
    .agg(
        count="count",
        average="mean",
        minimum="min",
        median="median",
        maximum="max",
    )
    .sort_values("average", ascending=False)
)

print(size_summary)


# ==================================================
# 9. BHK COUNTS
# ==================================================

print("\n========== BHK COUNTS ==========")

print(
    df["bhk"]
    .value_counts()
    .sort_index()
)


# ==================================================
# 10. BATHROOM COUNTS
# ==================================================

print("\n========== BATHROOM COUNTS ==========")

print(
    df["bathroom"]
    .value_counts()
    .sort_index()
)


# ==================================================
# 11. FURNISHING COUNTS
# ==================================================

print("\n========== FURNISHING STATUS ==========")

print(
    df["furnishing_status"]
    .value_counts()
)


# ==================================================
# 12. RENT OUTLIER CHECK
# ==================================================

q1 = df["rent"].quantile(0.25)
q3 = df["rent"].quantile(0.75)

iqr = q3 - q1

lower_limit = q1 - 1.5 * iqr
upper_limit = q3 + 1.5 * iqr

rent_outliers = df[
    (df["rent"] < lower_limit)
    | (df["rent"] > upper_limit)
]


print("\n========== RENT OUTLIER CHECK ==========")

print("Q1:", q1)

print("Q3:", q3)

print("IQR:", iqr)

print("Lower limit:", lower_limit)

print("Upper limit:", upper_limit)

print("Possible rent outliers:", len(rent_outliers))


# ==================================================
# 13. SHOW POSSIBLE RENT OUTLIERS
# ==================================================

if len(rent_outliers) > 0:

    print("\nPossible rent outlier records:")

    print(
        rent_outliers[
            [
                "standard_locality",
                "bhk",
                "rent",
                "size",
                "bathroom",
                "furnishing_status",
            ]
        ]
        .sort_values("rent", ascending=False)
        .to_string(index=False)
    )


# ==================================================
# 14. CHECK VERY LARGE PROPERTIES
# ==================================================

large_properties = df[
    df["size"] > 5000
]

print("\n========== VERY LARGE PROPERTIES ==========")

print("Properties above 5000 sq ft:", len(large_properties))

if len(large_properties) > 0:

    print(
        large_properties[
            [
                "standard_locality",
                "bhk",
                "rent",
                "size",
                "bathroom",
            ]
        ]
        .sort_values("size", ascending=False)
        .to_string(index=False)
    )


# ==================================================
# 15. CHECK UNUSUALLY HIGH BHK
# ==================================================

large_bhk = df[
    df["bhk"] > 6
]

print("\n========== HIGH BHK CHECK ==========")

print("Properties above 6 BHK:", len(large_bhk))

if len(large_bhk) > 0:

    print(
        large_bhk[
            [
                "standard_locality",
                "bhk",
                "rent",
                "size",
                "bathroom",
            ]
        ]
        .sort_values("bhk", ascending=False)
        .to_string(index=False)
    )


print("\n==================================================")
print("QUALITY CHECK COMPLETE")
print("==================================================")

print("\n========== EXTREME RENT RECORD ==========")

extreme_rent = df[
    df["rent"] == df["rent"].max()
]

print(
    extreme_rent.to_string(index=False)
)