import pandas as pd


def compare_current_market(
    input_file,
    target_locality,
    target_bhk,
    target_size,
    size_tolerance=0.20
):
    """
    Compare a target apartment with current rental listings.

    Parameters:
        input_file: path to cleaned live CSV
        target_locality: target Bangalore locality
        target_bhk: target BHK
        target_size: target apartment size in sqft
        size_tolerance: allowed size difference
                        0.20 means +/- 20%

    Returns:
        Dictionary containing market comparison results.
    """

    # ----------------------------------------------
    # 1. Load current listings
    # ----------------------------------------------

    df = pd.read_csv(input_file)

    # ----------------------------------------------
    # 2. Create lowercase locality text
    # ----------------------------------------------

    df["locality_text"] = (
        df["locality"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    target = target_locality.strip().lower()

    # ----------------------------------------------
    # 3. Match target locality
    # ----------------------------------------------

    locality_keywords = {
        "whitefield": "whitefield",
        "koramangala": "koramangala",
        "hsr layout": "hsr layout",
        "indiranagar": "indiranagar",
        "electronic city": "electronic city",
        "marathahalli": "marathahalli",
    }

    keyword = locality_keywords.get(target, target)

    # Electronic City sometimes appears as
    # "Electronics City"
    if target == "electronic city":
        locality_match = (
            df["locality_text"].str.contains(
                "electronic city|electronics city",
                regex=True,
                na=False
            )
        )
    else:
        locality_match = df["locality_text"].str.contains(
            keyword,
            regex=False,
            na=False
        )

    # ----------------------------------------------
    # 4. Match BHK
    # ----------------------------------------------

    df["bhk"] = pd.to_numeric(
        df["bhk"],
        errors="coerce"
    )

    bhk_match = df["bhk"] == target_bhk

    # ----------------------------------------------
    # 5. Match similar apartment size
    # ----------------------------------------------

    df["size_sqft"] = pd.to_numeric(
        df["size_sqft"],
        errors="coerce"
    )

    lower_size = target_size * (1 - size_tolerance)
    upper_size = target_size * (1 + size_tolerance)

    size_match = (
        (df["size_sqft"] >= lower_size)
        & (df["size_sqft"] <= upper_size)
    )

    # ----------------------------------------------
    # 6. Remove unavailable listings
    # ----------------------------------------------

    status_text = (
        df["availabilityStatus"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    unavailable_match = status_text.str.contains(
        "rented|timed out",
        regex=True,
        na=False
    )

    available_match = ~unavailable_match

    # ----------------------------------------------
    # 7. Build final comparable set
    # ----------------------------------------------

    comparables = df[
        locality_match
        & bhk_match
        & size_match
        & available_match
    ].copy()

    # ----------------------------------------------
    # 8. Calculate rent per sqft
    # ----------------------------------------------

    comparables["rent"] = pd.to_numeric(
        comparables["rent"],
        errors="coerce"
    )

    comparables = comparables[
        comparables["rent"] > 0
    ].copy()

    comparables["rent_per_sqft"] = (
        comparables["rent"]
        / comparables["size_sqft"]
    )

    # ----------------------------------------------
    # 9. Handle no comparable listings
    # ----------------------------------------------

    if len(comparables) == 0:
        return {
            "listing_count": 0,
            "median_rent": None,
            "q1_rent": None,
            "q3_rent": None,
            "median_rent_per_sqft": None,
            "comparables": comparables,
        }

    # ----------------------------------------------
    # 10. Calculate market statistics
    # ----------------------------------------------

    median_rent = comparables["rent"].median()
    q1_rent = comparables["rent"].quantile(0.25)
    q3_rent = comparables["rent"].quantile(0.75)

    median_rent_per_sqft = (
        comparables["rent_per_sqft"].median()
    )

    # ----------------------------------------------
    # 11. Return results
    # ----------------------------------------------

    return {
        "listing_count": len(comparables),
        "median_rent": median_rent,
        "q1_rent": q1_rent,
        "q3_rent": q3_rent,
        "median_rent_per_sqft": median_rent_per_sqft,
        "comparables": comparables,
    }