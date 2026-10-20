from prediction_engine import predict_rent


# ==================================================
# SAME APARTMENT, DIFFERENT FURNISHING
# ==================================================

locality = "Whitefield"
size_sqft = 1200
bhk = 2
bathrooms = 2


furnishing_options = [
    "Unfurnished",
    "Semi-Furnished",
    "Furnished",
]


print("==================================================")
print("FURNISHING SENSITIVITY TEST")
print("==================================================")


print("\nSame apartment:")
print(f"Locality: {locality}")
print(f"Size: {size_sqft} sq ft")
print(f"BHK: {bhk}")
print(f"Bathrooms: {bathrooms}")


for furnishing in furnishing_options:

    result = predict_rent(
        locality=locality,
        size_sqft=size_sqft,
        bhk=bhk,
        bathrooms=bathrooms,
        furnishing_status=furnishing,
    )

    print("\n--------------------------------------")

    print(
        f"Furnishing: {furnishing}"
    )

    print(
        f"Predicted rent: "
        f"₹{result['prediction']:,.0f}"
    )

    print(
        f"Approximate range: "
        f"₹{result['lower_rent']:,.0f}"
        f" – "
        f"₹{result['upper_rent']:,.0f}"
    )

    furnishing_contribution = (
        result["explanation"]
        .loc[
            result["explanation"]["feature"]
            == "Furnishing status",
            "contribution",
        ]
        .iloc[0]
    )

    print(
        f"Furnishing SHAP contribution: "
        f"₹{furnishing_contribution:,.0f}"
    )


print("\n==================================================")
print("FURNISHING TEST COMPLETE")
print("==================================================")