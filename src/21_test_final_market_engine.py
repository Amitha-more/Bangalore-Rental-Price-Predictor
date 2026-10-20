from importlib.util import spec_from_file_location, module_from_spec


# --------------------------------------------------
# Load the final market engine
# --------------------------------------------------

spec = spec_from_file_location(
    "final_market_engine",
    "src/20_final_market_engine.py"
)

module = module_from_spec(spec)

spec.loader.exec_module(module)


get_current_market_reference = (
    module.get_current_market_reference
)


# --------------------------------------------------
# Test apartment
# --------------------------------------------------

target_locality = "Whitefield"
target_bhk = 2
target_size = 1200


# --------------------------------------------------
# Run market comparison
# --------------------------------------------------

result = get_current_market_reference(
    target_locality=target_locality,
    target_bhk=target_bhk,
    target_size=target_size
)


# --------------------------------------------------
# Print results
# --------------------------------------------------

print("\n========================================")
print("FINAL CURRENT MARKET TEST")
print("========================================")

print(
    "Target locality:",
    target_locality
)

print(
    "Target BHK:",
    target_bhk
)

print(
    "Target size:",
    target_size,
    "sqft"
)

print(
    "\nComparable size range:",
    round(result["lower_size"]),
    "-",
    round(result["upper_size"]),
    "sqft"
)

print(
    "\nComparable listings:",
    result["listing_count"]
)


if result["listing_count"] > 0:

    print(
        "Sample quality:",
        result["sample_quality"]
    )

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

    print(
        "Median rent/sqft: ₹",
        round(
            result["median_rent_per_sqft"],
            2
        )
    )

    print(
        "Data refreshed:",
        result["data_refreshed"]
    )

else:

    print(
        "No comparable listings found."
    )