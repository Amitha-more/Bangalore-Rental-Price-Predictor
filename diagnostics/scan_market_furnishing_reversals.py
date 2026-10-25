"""
Market Furnishing-Price Reversal Diagnostic

Purpose:
    Scan the market comparison dataset for scenarios where semi-furnished
    median rent exceeds furnished median rent for the same locality, BHK,
    and target size.

Methodology:
    - Use existing market engine (src/23_furnishing_market_engine.py)
    - Test representative size targets for each locality × BHK combination
    - Compare medians across Unfurnished, Semi-Furnished, Furnished
    - Flag reversals (Semi > Furnished)
    - Report fallback scenarios and ambiguous availability statuses

Dataset: data/processed/all_live_clean_standardized.csv
Created: 2026-10-24
"""

import sys
from pathlib import Path

import pandas as pd

# Add src directory to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


from importlib.util import spec_from_file_location, module_from_spec

# Load the existing market engine.
engine_path = PROJECT_ROOT / "src" / "23_furnishing_market_engine.py"

spec = spec_from_file_location(
    "furnishing_market_engine",
    engine_path,
)

if spec is None or spec.loader is None:
    raise ImportError(
        f"Could not load market engine from: {engine_path}"
    )

market_module = module_from_spec(spec)
spec.loader.exec_module(market_module)

get_furnishing_market_reference = (
    market_module.get_furnishing_market_reference
)


# ==================================================
# 1. CONFIGURATION
# ==================================================

MARKET_DATA_FILE = (
    PROJECT_ROOT / "data" / "processed" / "all_live_clean_standardized.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_LOCALITIES = [
    "Whitefield",
    "Koramangala",
    "HSR Layout",
    "Indiranagar",
    "Electronic City",
    "Marathahalli",
]

FURNISHING_OPTIONS = ["Unfurnished", "Semi-Furnished", "Furnished"]


# ==================================================
# 2. LOAD AND ANALYZE MARKET DATA
# ==================================================

print("=" * 70)
print("MARKET FURNISHING-PRICE REVERSAL DIAGNOSTIC")
print("=" * 70)

print(f"\nLoading market data: {MARKET_DATA_FILE.name}")

df = pd.read_csv(MARKET_DATA_FILE)

print(f"Total listings: {len(df)}")

# Clean columns
df["target_locality"] = df["target_locality"].fillna("").astype(str).str.strip()
df["bhk"] = pd.to_numeric(df["bhk"], errors="coerce")
df["size_sqft"] = pd.to_numeric(df["size_sqft"], errors="coerce")
df["furnishing_status"] = df["furnishing_status"].fillna("").astype(str).str.strip()
df["availabilityStatus"] = df["availabilityStatus"].fillna("").astype(str).str.strip()

# Filter to supported localities
df = df[df["target_locality"].isin(SUPPORTED_LOCALITIES)]

print(f"Listings in supported localities: {len(df)}")

# Show distribution
print(f"\n{'=' * 70}")
print("LOCALITY × BHK DISTRIBUTION")
print(f"{'=' * 70}")

locality_bhk_counts = pd.crosstab(
    df["target_locality"],
    df["bhk"],
    margins=True,
    margins_name="Total"
)
print(locality_bhk_counts)


# ==================================================
# 3. DETERMINE REPRESENTATIVE TARGET SIZES
# ==================================================

print(f"\n{'=' * 70}")
print("REPRESENTATIVE TARGET SIZES")
print(f"{'=' * 70}")

# For each locality × BHK combination, use median size
test_scenarios = []

for locality in SUPPORTED_LOCALITIES:
    locality_df = df[df["target_locality"] == locality]

    for bhk in sorted(df["bhk"].dropna().unique()):
        bhk_df = locality_df[locality_df["bhk"] == bhk]

        if len(bhk_df) == 0:
            continue

        # Use median size as representative target
        median_size = bhk_df["size_sqft"].median()

        if pd.isna(median_size):
            continue

        # Round to nearest 50 for cleaner targets
        target_size = round(median_size / 50) * 50

        test_scenarios.append({
            "locality": locality,
            "bhk": int(bhk),
            "target_size": int(target_size),
            "listing_count": len(bhk_df)
        })

        print(f"  {locality:20} {int(bhk)} BHK: {int(target_size):>4} sq ft "
              f"(median of {len(bhk_df)} listings)")

print(f"\nTotal test scenarios: {len(test_scenarios)}")


# ==================================================
# 4. RUN MARKET ENGINE FOR EACH SCENARIO
# ==================================================

print(f"\n{'=' * 70}")
print("SCANNING MARKET COMPARISONS")
print(f"{'=' * 70}")

results = []
scenario_count = 0

for scenario in test_scenarios:
    locality = scenario["locality"]
    bhk = scenario["bhk"]
    target_size = scenario["target_size"]

    print(f"\n{locality}, {bhk} BHK, {target_size} sq ft:")

    scenario_results = {}

    for furnishing in FURNISHING_OPTIONS:

        market_result = get_furnishing_market_reference(
            target_locality=locality,
            target_bhk=bhk,
            target_size=target_size,
            target_furnishing=furnishing
        )

        # Count ambiguous availability statuses in selected comparables
        comparables = market_result["comparables"]

        ambiguous_count = 0
        if len(comparables) > 0:
            ambiguous_statuses = comparables["availabilityStatus"].str.lower()

            # Statuses that are not clearly available or unavailable
            ambiguous = (
                (ambiguous_statuses == "") |
                (ambiguous_statuses.str.contains("inc info", na=False)) |
                (ambiguous_statuses.str.contains("already listed", na=False)) |
                (ambiguous_statuses.str.contains("unknown", na=False))
            )
            ambiguous_count = ambiguous.sum()

        scenario_results[furnishing] = {
            "median_rent": market_result["median_rent"],
            "q1_rent": market_result["q1_rent"],
            "q3_rent": market_result["q3_rent"],
            "comparison_type": market_result["comparison_type"],
            "listing_count": market_result["listing_count"],
            "furnishing_listing_count": market_result["furnishing_listing_count"],
            "sample_quality": market_result["sample_quality"],
            "ambiguous_availability_count": ambiguous_count,
        }

        print(f"  {furnishing:15} → "
              f"{market_result['comparison_type']:25} | "
              f"Count: {market_result['listing_count']:>2} "
              f"(furnishing-specific: {market_result['furnishing_listing_count']:>2}) | "
              f"Median: {f'₹{market_result["median_rent"]:,.0f}' if market_result['median_rent'] else 'N/A':>12}")

    # Store combined result
    result = {
        "locality": locality,
        "bhk": bhk,
        "target_size": target_size,
    }

    for furnishing in FURNISHING_OPTIONS:
        prefix = furnishing.replace("-", "_").lower()
        result[f"{prefix}_median"] = scenario_results[furnishing]["median_rent"]
        result[f"{prefix}_q1"] = scenario_results[furnishing]["q1_rent"]
        result[f"{prefix}_q3"] = scenario_results[furnishing]["q3_rent"]
        result[f"{prefix}_comparison_type"] = scenario_results[furnishing]["comparison_type"]
        result[f"{prefix}_count"] = scenario_results[furnishing]["listing_count"]
        result[f"{prefix}_furnishing_count"] = scenario_results[furnishing]["furnishing_listing_count"]
        result[f"{prefix}_ambiguous_count"] = scenario_results[furnishing]["ambiguous_availability_count"]

    results.append(result)
    scenario_count += 1

results_df = pd.DataFrame(results)


# ==================================================
# 5. IDENTIFY FURNISHING-PRICE REVERSALS
# ==================================================

print(f"\n{'=' * 70}")
print("FURNISHING-PRICE REVERSAL ANALYSIS")
print(f"{'=' * 70}")

# Flag: Semi-Furnished median > Furnished median
results_df["semi_exceeds_furnished"] = (
    (results_df["semi_furnished_median"].notna()) &
    (results_df["furnished_median"].notna()) &
    (results_df["semi_furnished_median"] > results_df["furnished_median"])
)

# Flag: Different comparison groups used
results_df["different_comparison_groups"] = (
    results_df["semi_furnished_comparison_type"] !=
    results_df["furnished_comparison_type"]
)

# Flag: Either uses fallback
results_df["uses_fallback"] = (
    (results_df["semi_furnished_comparison_type"] == "All-furnishing fallback") |
    (results_df["furnished_comparison_type"] == "All-furnishing fallback") |
    (results_df["unfurnished_comparison_type"] == "All-furnishing fallback")
)

reversals = results_df[results_df["semi_exceeds_furnished"]]

print(f"\nScenarios examined: {scenario_count}")
print(f"Scenarios with Semi > Furnished reversal: {len(reversals)}")
print(f"Scenarios using fallback comparison: {results_df['uses_fallback'].sum()}")

if len(reversals) > 0:
    print(f"\n{'=' * 70}")
    print("FLAGGED REVERSALS (Semi-Furnished > Furnished)")
    print(f"{'=' * 70}")

    for idx, row in reversals.iterrows():
        print(f"\n{row['locality']}, {int(row['bhk'])} BHK, {int(row['target_size'])} sq ft:")

        print(f"  Unfurnished:    ₹{row['unfurnished_median']:>10,.0f} | "
              f"{row['unfurnished_comparison_type']:25} | "
              f"{int(row['unfurnished_count']):>2} listings "
              f"({int(row['unfurnished_furnishing_count'])} specific)")

        print(f"  Semi-Furnished: ₹{row['semi_furnished_median']:>10,.0f} | "
              f"{row['semi_furnished_comparison_type']:25} | "
              f"{int(row['semi_furnished_count']):>2} listings "
              f"({int(row['semi_furnished_furnishing_count'])} specific)")

        print(f"  Furnished:      ₹{row['furnished_median']:>10,.0f} | "
              f"{row['furnished_comparison_type']:25} | "
              f"{int(row['furnished_count']):>2} listings "
              f"({int(row['furnished_furnishing_count'])} specific)")

        delta = row['semi_furnished_median'] - row['furnished_median']
        print(f"  → Semi exceeds Furnished by ₹{delta:,.0f}")

        if row["different_comparison_groups"]:
            print(f"  ⚠ WARNING: Different comparison groups used")
            print(f"    Semi uses: {row['semi_furnished_comparison_type']}")
            print(f"    Furnished uses: {row['furnished_comparison_type']}")

        # Data quality warnings
        ambiguous_semi = int(row['semi_furnished_ambiguous_count'])
        ambiguous_furnished = int(row['furnished_ambiguous_count'])

        if ambiguous_semi > 0 or ambiguous_furnished > 0:
            print(f"  ⚠ DATA QUALITY: Ambiguous availability statuses found")
            if ambiguous_semi > 0:
                print(f"    Semi-Furnished: {ambiguous_semi} listings with unclear availability")
            if ambiguous_furnished > 0:
                print(f"    Furnished: {ambiguous_furnished} listings with unclear availability")


# ==================================================
# 6. FALLBACK SCENARIOS
# ==================================================

fallback_scenarios = results_df[results_df["uses_fallback"]]

if len(fallback_scenarios) > 0:
    print(f"\n{'=' * 70}")
    print("FALLBACK SCENARIOS (< 4 furnishing-specific comparables)")
    print(f"{'=' * 70}")

    for idx, row in fallback_scenarios.iterrows():
        print(f"\n{row['locality']}, {int(row['bhk'])} BHK, {int(row['target_size'])} sq ft:")

        for furnishing_key, furnishing_label in [
            ("unfurnished", "Unfurnished"),
            ("semi_furnished", "Semi-Furnished"),
            ("furnished", "Furnished")
        ]:
            comp_type = row[f"{furnishing_key}_comparison_type"]
            if comp_type == "All-furnishing fallback":
                furn_count = int(row[f"{furnishing_key}_furnishing_count"])
                total_count = int(row[f"{furnishing_key}_count"])
                print(f"  {furnishing_label:15} → Fallback "
                      f"(only {furn_count} specific, using all {total_count})")


# ==================================================
# 7. INTERPRETATION
# ==================================================

print(f"\n{'=' * 70}")
print("INTERPRETATION")
print(f"{'=' * 70}")

if len(reversals) > 0:
    print("\nFlagged reversals MAY indicate:")
    print("  1. Actual market pattern where semi-furnished commands premium")
    print("     (e.g., modular kitchens, wardrobes without full furniture)")
    print("  2. Different comparison groups used (furnishing-specific vs fallback)")
    print("     making medians non-comparable")
    print("  3. Small sample sizes leading to unstable median estimates")
    print("  4. Ambiguous availability statuses including unavailable listings")
    print("  5. Data collection timing differences between furnishing categories")

    print("\nReversals DO NOT automatically indicate:")
    print("  ✗ A bug in the market engine")
    print("  ✗ Incorrect ML model predictions")
    print("  ✗ Invalid data that should be deleted")

    different_groups = reversals["different_comparison_groups"].sum()
    if different_groups > 0:
        print(f"\n⚠ IMPORTANT: {different_groups} of {len(reversals)} reversals use different")
        print("  comparison groups. These medians are NOT directly comparable:")
        print("  - One uses 4+ furnishing-specific listings")
        print("  - Other uses all-furnishing fallback (mixed furnishing types)")
        print("  This is an expected limitation when data is sparse.")

else:
    print("\n✓ No Semi > Furnished reversals detected in current market data.")
    print("  All medians follow expected ordering or have insufficient data.")

if fallback_scenarios["uses_fallback"].sum() > 0:
    fallback_count = len(fallback_scenarios)
    print(f"\n⚠ {fallback_count} scenario(s) use all-furnishing fallback due to")
    print("  insufficient furnishing-specific comparables (< 4 listings).")
    print("  These medians aggregate across multiple furnishing types.")


# ==================================================
# 8. SAVE RESULTS
# ==================================================

output_file = OUTPUT_DIR / "market_furnishing_scan_results.csv"
results_df.to_csv(output_file, index=False)

reversal_file = OUTPUT_DIR / "market_furnishing_reversals.csv"
if len(reversals) > 0:
    reversals.to_csv(reversal_file, index=False)
    print(f"\n{'=' * 70}")
    print("RESULTS SAVED")
    print(f"{'=' * 70}")
    print(f"  Full results: {output_file}")
    print(f"  Reversals only: {reversal_file}")
else:
    print(f"\n{'=' * 70}")
    print("RESULTS SAVED")
    print(f"{'=' * 70}")
    print(f"  Full results: {output_file}")
    print(f"  No reversals file created (none detected)")


# ==================================================
# 9. SUMMARY
# ==================================================

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")

print(f"\nScenarios examined: {scenario_count}")
print(f"Flagged reversals (Semi > Furnished): {len(reversals)}")
print(f"Scenarios with fallback comparisons: {fallback_scenarios['uses_fallback'].sum()}")

total_ambiguous = (
    results_df["unfurnished_ambiguous_count"].sum() +
    results_df["semi_furnished_ambiguous_count"].sum() +
    results_df["furnished_ambiguous_count"].sum()
)
print(f"Total listings with ambiguous availability: {int(total_ambiguous)}")

print("\nThis diagnostic does NOT:")
print("  ✗ Modify source code or production datasets")
print("  ✗ Automatically fix or remove data")
print("  ✗ Change ML model predictions")
print("  ✗ Alter market engine filtering rules")

print(f"\n{'=' * 70}")
print("DIAGNOSTIC COMPLETE")
print(f"{'=' * 70}\n")
