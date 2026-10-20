from importlib.util import spec_from_file_location, module_from_spec

from src.prediction_engine import predict_rent


# --------------------------------------------------
# Load furnishing-aware market engine
# --------------------------------------------------

spec = spec_from_file_location(
    "furnishing_market_engine",
    "src/23_furnishing_market_engine.py"
)

market_module = module_from_spec(spec)
spec.loader.exec_module(market_module)

get_furnishing_market_reference = (
    market_module.get_furnishing_market_reference
)


# --------------------------------------------------
# Unified prediction function
# --------------------------------------------------

def get_rental_assessment(
    locality,
    size_sqft,
    bhk,
    bathrooms,
    furnishing_status
):
    """
    Combines:

    1. Historical ML prediction
    2. ML prediction range
    3. SHAP explanation
    4. Current market reference
    5. Furnishing-aware market comparison
    """

    # --------------------------------------------------
    # 1. Historical ML prediction
    # --------------------------------------------------

    ml_result = predict_rent(
        locality=locality,
        size_sqft=size_sqft,
        bhk=bhk,
        bathrooms=bathrooms,
        furnishing_status=furnishing_status
    )

    # --------------------------------------------------
    # 2. Current market reference
    # --------------------------------------------------

    market_result = (
        get_furnishing_market_reference(
            target_locality=locality,
            target_bhk=bhk,
            target_size=size_sqft,
            target_furnishing=furnishing_status
        )
    )

    # --------------------------------------------------
    # 3. Compare ML estimate with current market
    # --------------------------------------------------

    market_median = market_result["median_rent"]

    comparison = None

    if market_median is not None:

        if ml_result["prediction"] < market_median:
            comparison = "Below current market median"

        elif ml_result["prediction"] > market_median:
            comparison = "Above current market median"

        else:
            comparison = "Close to current market median"

    # --------------------------------------------------
    # 4. Return unified result
    # --------------------------------------------------

    return {
        "ml_prediction": ml_result["prediction"],
        "ml_lower_rent": ml_result["lower_rent"],
        "ml_upper_rent": ml_result["upper_rent"],
        "shap_explanation": ml_result["explanation"],
        "base_value": ml_result["base_value"],

        "market_listing_count": (
            market_result["listing_count"]
        ),

        "market_furnishing_listing_count": (
            market_result[
                "furnishing_listing_count"
            ]
        ),

        "market_median_rent": (
            market_result["median_rent"]
        ),

        "market_q1_rent": (
            market_result["q1_rent"]
        ),

        "market_q3_rent": (
            market_result["q3_rent"]
        ),

        "market_median_rent_per_sqft": (
            market_result[
                "median_rent_per_sqft"
            ]
        ),

        "market_comparison_type": (
            market_result["comparison_type"]
        ),

        "market_sample_quality": (
            market_result["sample_quality"]
        ),

        "market_furnishing_breakdown": (
            market_result[
                "furnishing_breakdown"
            ]
        ),

        "market_data_refreshed": (
            market_result["data_refreshed"]
        ),

        "comparison_to_market": comparison,
    }