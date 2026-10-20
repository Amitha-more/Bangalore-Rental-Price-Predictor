from prediction_engine import predict_rent


# ==================================================
# TEST APARTMENT
# ==================================================

result = predict_rent(
    locality="Whitefield",
    size_sqft=1200,
    bhk=2,
    bathrooms=2,
    furnishing_status="Semi-Furnished",
)


# ==================================================
# SHOW RESULT
# ==================================================

print("==================================================")
print("PREDICTION ENGINE TEST")
print("==================================================")


print(
    f"\nPredicted rent: "
    f"₹{result['prediction']:,.0f}"
)


print(
    f"Approximate lower range: "
    f"₹{result['lower_rent']:,.0f}"
)


print(
    f"Approximate upper range: "
    f"₹{result['upper_rent']:,.0f}"
)


print(
    "\n========== EXPLANATION =========="
)


print(
    result["explanation"].to_string(
        index=False
    )
)


print(
    "\n=================================================="
)

print(
    "PREDICTION ENGINE TEST COMPLETE"
)

print(
    "=================================================="
)