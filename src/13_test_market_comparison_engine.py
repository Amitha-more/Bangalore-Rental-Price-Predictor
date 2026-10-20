from market_comparison_engine import compare_current_market


# --------------------------------------------------
# Test apartment
# --------------------------------------------------

input_file = (
    "data/processed/"
    "whitefield_2bhk_comparables.csv"
)

target_locality = "Whitefield"
target_bhk = 2
target_size = 1200


# --------------------------------------------------
# Run market comparison
# --------------------------------------------------

result = compare_current_market(
    input_file=input_file,
    target_locality=target_locality,
    target_bhk=target_bhk,
    target_size=target_size
)


# --------------------------------------------------
# Print results
# --------------------------------------------------

print("Target apartment:")
print("Locality:", target_locality)
print("BHK:", target_bhk)
print("Size:", target_size, "sqft")

print(
    "\nActive comparable listings:",
    result["listing_count"]
)

print("\nCurrent market reference:")

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

    print(
        "Median rent per sqft: ₹",
        round(result["median_rent_per_sqft"], 2)
    )

else:

    print("No comparable listings found.")