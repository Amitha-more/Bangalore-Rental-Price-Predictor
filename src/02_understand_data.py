from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. Find our project folder
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Location of our raw dataset
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "house_rent_raw.csv"


# --------------------------------------------------
# 2. Load the dataset
# --------------------------------------------------

df = pd.read_csv(RAW_FILE)


# --------------------------------------------------
# 3. Show all cities
# --------------------------------------------------

print("\n========== ALL CITIES ==========")

print(df["City"].value_counts())


# --------------------------------------------------
# 4. Create Bangalore-only data
# --------------------------------------------------

bangalore_df = df[
    df["City"].str.strip().str.lower() == "bangalore"
].copy()


print("\n========== BANGALORE DATA ==========")

print("Number of Bangalore properties:", len(bangalore_df))


# --------------------------------------------------
# 5. Show Bangalore localities
# --------------------------------------------------

print("\n========== BANGALORE LOCALITIES ==========")

print(
    bangalore_df["Area Locality"]
    .value_counts()
    .head(30)
)


# --------------------------------------------------
# 6. Check our six target localities
# --------------------------------------------------

target_localities = [
    "Whitefield",
    "Koramangala",
    "HSR Layout",
    "Indiranagar",
    "Electronic City",
    "Marathahalli",
]


print("\n========== EXACT LOCALITY MATCHES ==========")

for locality in target_localities:

    count = (
        bangalore_df["Area Locality"]
        .str.strip()
        .str.lower()
        == locality.lower()
    ).sum()

    print(f"{locality}: {count}")


# --------------------------------------------------
# 7. Find possible variations of each locality
# --------------------------------------------------

search_terms = {
    "Whitefield": "whitefield",
    "Koramangala": "koramangala",
    "HSR Layout": "hsr",
    "Indiranagar": "indira",
    "Electronic City": "electronic",
    "Marathahalli": "marathahalli",
}


print("\n========== LOCALITY VARIATIONS ==========")

for locality, search_word in search_terms.items():

    matches = bangalore_df[
        bangalore_df["Area Locality"]
        .str.contains(search_word, case=False, na=False)
    ]

    print(f"\n--- {locality} ---")

    if len(matches) == 0:
        print("No matching locality names found.")
    else:
        print(
            matches["Area Locality"]
            .value_counts()
        )