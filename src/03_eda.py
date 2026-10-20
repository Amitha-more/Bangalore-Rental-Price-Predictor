from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==================================================
# 1. PROJECT FILE LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rentals_clean.csv"
)

FIGURE_DIR = (
    PROJECT_ROOT
    / "reports"
    / "figures"
)

FIGURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# 2. LOAD CLEAN DATA
# ==================================================

df = pd.read_csv(CLEAN_FILE)


print("==================================================")
print("EXPLORATORY DATA ANALYSIS")
print("==================================================")


print("\nDataset shape:")

print(df.shape)


# ==================================================
# 3. BASIC SUMMARY
# ==================================================

print("\n========== BASIC STATISTICS ==========")

print(
    df[
        [
            "rent",
            "size",
            "bhk",
            "bathroom",
            "rent_per_sqft"
        ]
    ].describe()
)


# ==================================================
# 4. AVERAGE AND MEDIAN RENT BY LOCALITY
# ==================================================

print("\n========== RENT BY LOCALITY ==========")

locality_rent = (
    df
    .groupby("standard_locality")["rent"]
    .agg(
        count="count",
        average_rent="mean",
        median_rent="median"
    )
    .sort_values(
        "median_rent",
        ascending=False
    )
)

print(locality_rent)


# ==================================================
# 5. CHART 1 — RENT DISTRIBUTION
# ==================================================

plt.figure(figsize=(9, 5))

sns.histplot(
    data=df,
    x="rent",
    bins=25,
    kde=True
)

plt.title(
    "Monthly rent distribution"
)

plt.xlabel(
    "Monthly rent (INR)"
)

plt.ylabel(
    "Number of properties"
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "01_rent_distribution.png",
    dpi=150
)

plt.close()


# ==================================================
# 6. CHART 2 — RENT BY LOCALITY
# ==================================================

locality_order = (
    df
    .groupby("standard_locality")["rent"]
    .median()
    .sort_values(
        ascending=False
    )
    .index
)

plt.figure(figsize=(10, 5))

sns.boxplot(
    data=df,
    x="standard_locality",
    y="rent",
    order=locality_order
)

plt.title(
    "Rent distribution by locality"
)

plt.xlabel(
    "Locality"
)

plt.ylabel(
    "Monthly rent (INR)"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "02_rent_by_locality.png",
    dpi=150
)

plt.close()


# ==================================================
# 7. CHART 3 — RENT VS SIZE
# ==================================================

plt.figure(figsize=(9, 5))

sns.scatterplot(
    data=df,
    x="size",
    y="rent",
    hue="standard_locality"
)

plt.title(
    "Monthly rent vs apartment size"
)

plt.xlabel(
    "Size (sq ft)"
)

plt.ylabel(
    "Monthly rent (INR)"
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "03_rent_vs_size.png",
    dpi=150
)

plt.close()


# ==================================================
# 8. CHART 4 — RENT BY BHK
# ==================================================

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="bhk",
    y="rent"
)

plt.title(
    "Rent distribution by BHK"
)

plt.xlabel(
    "BHK"
)

plt.ylabel(
    "Monthly rent (INR)"
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "04_rent_by_bhk.png",
    dpi=150
)

plt.close()


# ==================================================
# 9. CHART 5 — RENT BY FURNISHING
# ==================================================

furnishing_order = [
    "Unfurnished",
    "Semi-Furnished",
    "Furnished"
]

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="furnishing_status",
    y="rent",
    order=furnishing_order
)

plt.title(
    "Rent distribution by furnishing status"
)

plt.xlabel(
    "Furnishing status"
)

plt.ylabel(
    "Monthly rent (INR)"
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "05_rent_by_furnishing.png",
    dpi=150
)

plt.close()


# ==================================================
# 10. CHART 6 — RENT PER SQ FT BY LOCALITY
# ==================================================

plt.figure(figsize=(10, 5))

sns.boxplot(
    data=df,
    x="standard_locality",
    y="rent_per_sqft",
    order=locality_order
)

plt.title(
    "Rent per sq ft by locality"
)

plt.xlabel(
    "Locality"
)

plt.ylabel(
    "Rent per sq ft"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "06_rent_per_sqft_by_locality.png",
    dpi=150
)

plt.close()


# ==================================================
# 11. SAVE LOCALITY SUMMARY
# ==================================================

locality_rent.to_csv(
    FIGURE_DIR / "locality_rent_summary.csv"
)


# ==================================================
# 12. FINISHED
# ==================================================

print(
    "\nEDA charts saved to:"
)

print(FIGURE_DIR)

print(
    "\nEDA COMPLETE!"
)