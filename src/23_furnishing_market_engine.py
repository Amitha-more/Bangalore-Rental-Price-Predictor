import pandas as pd
from pathlib import Path


def get_furnishing_market_reference(
    target_locality,
    target_bhk,
    target_size,
    target_furnishing,
    size_tolerance=0.20,
    min_furnishing_comparables=4
):
    """
    Get a current-market reference with
    furnishing-aware comparison.

    The engine first finds comparable listings
    using locality, BHK and size.

    It then tries to use the requested furnishing
    category when enough comparable listings exist.

    Otherwise, it falls back to all furnishing
    categories.
    """

    # --------------------------------------------------
    # 1. Load standardized live dataset
    # --------------------------------------------------

    input_file = Path(
        "data/processed/"
        "all_live_clean_standardized.csv"
    )

    df = pd.read_csv(input_file)

    # --------------------------------------------------
    # 2. Clean important columns
    # --------------------------------------------------

    df["target_locality"] = (
        df["target_locality"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["furnishing_status"] = (
        df["furnishing_status"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["availabilityStatus"] = (
        df["availabilityStatus"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["bhk"] = pd.to_numeric(
        df["bhk"],
        errors="coerce"
    )

    df["size_sqft"] = pd.to_numeric(
        df["size_sqft"],
        errors="coerce"
    )

    df["rent"] = pd.to_numeric(
        df["rent"],
        errors="coerce"
    )

    # --------------------------------------------------
    # 3. Match locality + BHK
    # --------------------------------------------------

    comparables = df[
        (df["target_locality"] == target_locality)
        & (df["bhk"] == target_bhk)
    ].copy()

    # --------------------------------------------------
    # 4. Match similar size
    # --------------------------------------------------

    lower_size = (
        target_size * (1 - size_tolerance)
    )

    upper_size = (
        target_size * (1 + size_tolerance)
    )

    comparables = comparables[
        (comparables["size_sqft"] >= lower_size)
        & (comparables["size_sqft"] <= upper_size)
    ].copy()

    # --------------------------------------------------
    # 5. Remove unavailable listings
    # --------------------------------------------------

    status_text = (
        comparables["availabilityStatus"]
        .str.lower()
    )

    unavailable = status_text.str.contains(
        "rented|timed out",
        regex=True,
        na=False
    )

    comparables = comparables[
        ~unavailable
    ].copy()

    # --------------------------------------------------
    # 6. Remove invalid rents
    # --------------------------------------------------

    comparables = comparables[
        (comparables["rent"] >= 5000)
        & (comparables["size_sqft"] > 0)
    ].copy()

    # --------------------------------------------------
    # 7. No general comparables
    # --------------------------------------------------

    if len(comparables) == 0:

        return {
            "listing_count": 0,
            "furnishing_listing_count": 0,
            "median_rent": None,
            "q1_rent": None,
            "q3_rent": None,
            "median_rent_per_sqft": None,
            "comparison_type": "No comparable listings",
            "sample_quality": "Very limited",
            "lower_size": lower_size,
            "upper_size": upper_size,
            "data_refreshed": None,
            "furnishing_breakdown": {},
            "comparables": comparables,
        }

    # --------------------------------------------------
    # 8. Calculate rent per sqft
    # --------------------------------------------------

    comparables["rent_per_sqft"] = (
        comparables["rent"]
        / comparables["size_sqft"]
    )

    # --------------------------------------------------
    # 9. Furnishing breakdown
    # --------------------------------------------------

    furnishing_breakdown = (
        comparables["furnishing_status"]
        .replace("", "Unknown")
        .value_counts()
        .to_dict()
    )

    # --------------------------------------------------
    # 10. Try furnishing-specific comparables
    # --------------------------------------------------

    furnishing_comparables = comparables[
        comparables["furnishing_status"]
        .str.lower()
        == target_furnishing.strip().lower()
    ].copy()

    furnishing_count = len(
        furnishing_comparables
    )

    # --------------------------------------------------
    # 11. Decide whether to use furnishing-specific
    #     or all-furnishing comparison
    # --------------------------------------------------

    if furnishing_count >= min_furnishing_comparables:

        selected = furnishing_comparables

        comparison_type = (
            "Furnishing-specific"
        )

    else:

        selected = comparables

        comparison_type = (
            "All-furnishing fallback"
        )

    # --------------------------------------------------
    # 12. Calculate final market statistics
    # --------------------------------------------------

    median_rent = (
        selected["rent"].median()
    )

    q1_rent = (
        selected["rent"].quantile(0.25)
    )

    q3_rent = (
        selected["rent"].quantile(0.75)
    )

    median_rent_per_sqft = (
        selected["rent_per_sqft"].median()
    )

    listing_count = len(selected)

    # --------------------------------------------------
    # 13. Sample quality
    # --------------------------------------------------

    if listing_count >= 8:

        sample_quality = "Good"

    elif listing_count >= 4:

        sample_quality = "Limited"

    else:

        sample_quality = "Very limited"

    # --------------------------------------------------
    # 14. Latest data refresh
    # --------------------------------------------------

    data_refreshed = None

    if "fetched_at" in selected.columns:

        fetched_times = pd.to_datetime(
            selected["fetched_at"],
            errors="coerce",
            utc=True
        )

        if fetched_times.notna().any():

            data_refreshed = (
                fetched_times.max().isoformat()
            )

    # --------------------------------------------------
    # 15. Return results
    # --------------------------------------------------

    return {
        "listing_count": listing_count,
        "furnishing_listing_count": furnishing_count,
        "median_rent": median_rent,
        "q1_rent": q1_rent,
        "q3_rent": q3_rent,
        "median_rent_per_sqft": median_rent_per_sqft,
        "comparison_type": comparison_type,
        "sample_quality": sample_quality,
        "lower_size": lower_size,
        "upper_size": upper_size,
        "data_refreshed": data_refreshed,
        "furnishing_breakdown": furnishing_breakdown,
        "comparables": selected,
    }