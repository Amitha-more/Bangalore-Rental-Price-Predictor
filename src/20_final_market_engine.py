import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Final Current-Market Comparison Engine
# --------------------------------------------------

def get_current_market_reference(
    target_locality,
    target_bhk,
    target_size,
    size_tolerance=0.20
):
    """
    Returns a current market reference for an apartment.

    Parameters
    ----------
    target_locality : str
        One of the six supported Bangalore localities.

    target_bhk : int
        Target BHK: 1, 2, 3 or 4.

    target_size : float
        Apartment size in square feet.

    size_tolerance : float
        Default 0.20 means +/- 20% of target size.

    Returns
    -------
    dict
        Market reference information.
    """

    # --------------------------------------------------
    # 1. Load final standardized live dataset
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
    # 3. Match locality and BHK
    # --------------------------------------------------

    comparables = df[
        (df["target_locality"] == target_locality)
        & (df["bhk"] == target_bhk)
    ].copy()

    # --------------------------------------------------
    # 4. Match similar apartment size
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
        .fillna("")
        .astype(str)
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
    # 6. Remove invalid rent / size
    # --------------------------------------------------

    comparables = comparables[
        (comparables["rent"] >= 5000)
        & (comparables["size_sqft"] > 0)
    ].copy()

    # --------------------------------------------------
    # 7. No comparable listings
    # --------------------------------------------------

    if len(comparables) == 0:

        return {
            "listing_count": 0,
            "median_rent": None,
            "q1_rent": None,
            "q3_rent": None,
            "median_rent_per_sqft": None,
            "lower_size": lower_size,
            "upper_size": upper_size,
            "data_refreshed": None,
            "comparables": comparables,
        }

    # --------------------------------------------------
    # 8. Calculate rent per square foot
    # --------------------------------------------------

    comparables["rent_per_sqft"] = (
        comparables["rent"]
        / comparables["size_sqft"]
    )

    # --------------------------------------------------
    # 9. Calculate market statistics
    # --------------------------------------------------

    median_rent = (
        comparables["rent"].median()
    )

    q1_rent = (
        comparables["rent"].quantile(0.25)
    )

    q3_rent = (
        comparables["rent"].quantile(0.75)
    )

    median_rent_per_sqft = (
        comparables["rent_per_sqft"].median()
    )

    # --------------------------------------------------
    # 10. Find latest data refresh time
    # --------------------------------------------------

    data_refreshed = None

    if "fetched_at" in comparables.columns:

        fetched_times = pd.to_datetime(
            comparables["fetched_at"],
            errors="coerce",
            utc=True
        )

        if fetched_times.notna().any():

            data_refreshed = (
                fetched_times.max().isoformat()
            )

    # --------------------------------------------------
    # 11. Determine sample-size message
    # --------------------------------------------------

    listing_count = len(comparables)

    if listing_count >= 8:
        sample_quality = "Good"
    elif listing_count >= 4:
        sample_quality = "Limited"
    else:
        sample_quality = "Very limited"

    # --------------------------------------------------
    # 12. Return final result
    # --------------------------------------------------

    return {
        "listing_count": listing_count,
        "median_rent": median_rent,
        "q1_rent": q1_rent,
        "q3_rent": q3_rent,
        "median_rent_per_sqft": median_rent_per_sqft,
        "lower_size": lower_size,
        "upper_size": upper_size,
        "data_refreshed": data_refreshed,
        "sample_quality": sample_quality,
        "comparables": comparables,
    }