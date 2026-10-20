from importlib.util import spec_from_file_location, module_from_spec


# --------------------------------------------------
# Load furnishing-aware market engine
# --------------------------------------------------

spec = spec_from_file_location(
    "furnishing_market_engine",
    "src/23_furnishing_market_engine.py"
)

module = module_from_spec(spec)
spec.loader.exec_module(module)

get_furnishing_market_reference = (
    module.get_furnishing_market_reference
)


# --------------------------------------------------
# Test apartment
# --------------------------------------------------

target_locality = "Whitefield"
target_bhk = 2
target_size = 1200


furnishing_options = [
    "Unfurnished",
    "Semi-Furnished",
    "Furnished",
]


# --------------------------------------------------
# Test all furnishing categories
# --------------------------------------------------

print("\n========================================")
print("FURNISHING-AWARE MARKET TEST")
print("========================================")


for furnishing in furnishing_options:

    result = get_furnishing_market_reference(
        target_locality=target_locality,
        target_bhk=target_bhk,
        target_size=target_size,
        target_furnishing=furnishing
    )

    print(
        f"\n{target_locality} | "
        f"{target_bhk} BHK | "
        f"{target_size} sqft | "
        f"{furnishing}"
    )

    print(
        "Furnishing listings found:",
        result["furnishing_listing_count"]
    )

    print(
        "Listings used:",
        result["listing_count"]
    )

    print(
        "Comparison:",
        result["comparison_type"]
    )

    print(
        "Sample quality:",
        result["sample_quality"]
    )

    if result["listing_count"] > 0:

        print(
            "Median rent: ₹",
            round(result["median_rent"])
        )

        print(
            "Q1 rent: ₹",
            round(result["q1_rent"])
        )

        print(
            "Q3 rent: ₹",
            round(result["q3_rent"])
        )

    else:

        print(
            "No comparable listings found."
        )


# --------------------------------------------------
# Show overall furnishing distribution
# --------------------------------------------------

print("\n========================================")
print("FURNISHING BREAKDOWN")
print("========================================")


result = get_furnishing_market_reference(
    target_locality=target_locality,
    target_bhk=target_bhk,
    target_size=target_size,
    target_furnishing="Semi-Furnished"
)


print(
    result["furnishing_breakdown"]
)