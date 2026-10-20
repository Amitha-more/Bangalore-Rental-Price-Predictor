from prediction_engine import predict_rent


# --------------------------------------------------
# Test property
# --------------------------------------------------

locality = "Whitefield"
size_sqft = 1200
bhk = 2
bathrooms = 2
furnishing_status = "Semi-Furnished"


# --------------------------------------------------
# Run existing ML prediction engine
# --------------------------------------------------

result = predict_rent(
    locality=locality,
    size_sqft=size_sqft,
    bhk=bhk,
    bathrooms=bathrooms,
    furnishing_status=furnishing_status
)


# --------------------------------------------------
# Inspect the result
# --------------------------------------------------

print("\n========================================")
print("EXISTING ML ENGINE OUTPUT")
print("========================================")

print("Result type:")
print(type(result).__name__)


if isinstance(result, dict):

    print("\nDictionary keys:")
    print(list(result.keys()))

    print("\nValues:")

    for key, value in result.items():

        print(
            f"\n{key}:"
        )

        print(value)

else:

    print("\nComplete result:")
    print(result)