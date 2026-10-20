from importlib.util import spec_from_file_location, module_from_spec


# --------------------------------------------------
# Load final market engine
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
# Test combinations
# --------------------------------------------------

tests = [
    ("Whitefield", 1, 800),
    ("Whitefield", 2, 1200),
    ("Whitefield", 3, 1500),
    ("Whitefield", 4, 2000),

    ("Koramangala", 1, 700),
    ("Koramangala", 2, 1200),
    ("Koramangala", 3, 1600),
    ("Koramangala", 4, 2000),

    ("HSR Layout", 1, 700),
    ("HSR Layout", 2, 1200),
    ("HSR Layout", 3, 1600),
    ("HSR Layout", 4, 2000),

    ("Indiranagar", 1, 700),
    ("Indiranagar", 2, 1200),
    ("Indiranagar", 3, 1600),
    ("Indiranagar", 4, 2000),

    ("Electronic City", 1, 700),
    ("Electronic City", 2, 1200),
    ("Electronic City", 3, 1600),
    ("Electronic City", 4, 2000),

    ("Marathahalli", 1, 700),
    ("Marathahalli", 2, 1200),
    ("Marathahalli", 3, 1600),
    ("Marathahalli", 4, 2000),
]


# --------------------------------------------------
# Run tests
# --------------------------------------------------

print("\n========================================")
print("ALL LOCALITY + BHK MARKET TESTS")
print("========================================")

for locality, bhk, size in tests:

    result = get_current_market_reference(
        target_locality=locality,
        target_bhk=bhk,
        target_size=size
    )

    print(
        f"\n{locality} | {bhk} BHK | {size} sqft"
    )

    print(
        "Comparables:",
        result["listing_count"]
    )

    if result["listing_count"] > 0:

        print(
            "Median: ₹",
            round(result["median_rent"])
        )

        print(
            "Range: ₹",
            round(result["q1_rent"]),
            "- ₹",
            round(result["q3_rent"])
        )

        print(
            "Sample:",
            result["sample_quality"]
        )

    else:

        print(
            "No comparable listings found."
        )