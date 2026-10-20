from importlib.util import spec_from_file_location, module_from_spec


# --------------------------------------------------
# Load unified engine
# --------------------------------------------------

spec = spec_from_file_location(
    "unified_engine",
    "src/26_unified_prediction_engine.py"
)

module = module_from_spec(spec)
spec.loader.exec_module(module)

get_rental_assessment = (
    module.get_rental_assessment
)


# --------------------------------------------------
# Test apartment
# --------------------------------------------------

result = get_rental_assessment(
    locality="Whitefield",
    size_sqft=1200,
    bhk=2,
    bathrooms=2,
    furnishing_status="Semi-Furnished"
)


# --------------------------------------------------
# Print final assessment
# --------------------------------------------------

print("\n========================================")
print("UNIFIED RENTAL ASSESSMENT")
print("========================================")

print("\nML MODEL")
print("----------------------------------------")

print(
    "ML prediction: ₹",
    round(result["ml_prediction"])
)

print(
    "ML lower range: ₹",
    round(result["ml_lower_rent"])
)

print(
    "ML upper range: ₹",
    round(result["ml_upper_rent"])
)


print("\nCURRENT MARKET")
print("----------------------------------------")

print(
    "Comparable listings:",
    result["market_listing_count"]
)

print(
    "Furnishing-specific listings:",
    result[
        "market_furnishing_listing_count"
    ]
)

print(
    "Median market rent: ₹",
    round(result["market_median_rent"])
)

print(
    "Q1 market rent: ₹",
    round(result["market_q1_rent"])
)

print(
    "Q3 market rent: ₹",
    round(result["market_q3_rent"])
)

print(
    "Median rent/sqft: ₹",
    round(
        result[
            "market_median_rent_per_sqft"
        ],
        2
    )
)

print(
    "Comparison type:",
    result["market_comparison_type"]
)

print(
    "Sample quality:",
    result["market_sample_quality"]
)

print(
    "Comparison to ML:",
    result["comparison_to_market"]
)


print("\nFURNISHING BREAKDOWN")
print("----------------------------------------")

print(
    result[
        "market_furnishing_breakdown"
    ]
)


print("\nDATA REFRESH")
print("----------------------------------------")

print(
    result["market_data_refreshed"]
)


print("\nSHAP EXPLANATION")
print("----------------------------------------")

print(
    result["shap_explanation"].to_string(
        index=False
    )
)