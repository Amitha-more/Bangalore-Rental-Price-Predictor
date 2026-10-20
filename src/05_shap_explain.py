from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap


# ==================================================
# 1. FILE LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "final_model.joblib"
)

MODEL_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_data.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "figures"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# 2. LOAD MODEL AND DATA
# ==================================================

model = joblib.load(
    MODEL_FILE
)

df = pd.read_csv(
    MODEL_DATA_FILE
)


# ==================================================
# 3. SELECT MODEL INPUT COLUMNS
# ==================================================

feature_columns = [
    "locality",
    "size_sqft",
    "bhk",
    "bathrooms",
    "furnishing_status",
]

X = df[
    feature_columns
].copy()


# ==================================================
# 4. GET PREPROCESSOR AND LINEAR REGRESSION MODEL
# ==================================================

preprocessor = model.named_steps[
    "preprocessor"
]

linear_regressor = model.named_steps[
    "model"
]


# ==================================================
# 5. TRANSFORM THE DATA
# ==================================================

X_transformed = preprocessor.transform(
    X
)


# ==================================================
# 6. GET TRANSFORMED FEATURE NAMES
# ==================================================

transformed_feature_names = (
    preprocessor
    .get_feature_names_out()
)


print("==================================================")
print("SHAP EXPLAINABILITY")
print("==================================================")


print("\n========== TRANSFORMED FEATURES ==========")

for name in transformed_feature_names:
    print(name)


# ==================================================
# 7. SELECT ONE EXAMPLE PROPERTY
# ==================================================

example = X.iloc[[0]].copy()


print("\n========== EXAMPLE PROPERTY ==========")

print(
    example.to_string(index=False)
)


# ==================================================
# 8. TRANSFORM EXAMPLE
# ==================================================

example_transformed = (
    preprocessor.transform(
        example
    )
)


# ==================================================
# 9. CREATE SHAP BACKGROUND
# ==================================================

background_size = min(
    30,
    len(X)
)

background = X.sample(
    n=background_size,
    random_state=42
)

background_transformed = (
    preprocessor.transform(
        background
    )
)


# ==================================================
# 10. CREATE LINEAR SHAP EXPLAINER
# ==================================================

print(
    "\nCreating LinearExplainer..."
)

explainer = shap.LinearExplainer(
    linear_regressor,
    background_transformed,
)


# ==================================================
# 11. CALCULATE SHAP VALUES
# ==================================================

shap_result = explainer(
    example_transformed
)


# ==================================================
# 12. GET MODEL PREDICTION
# ==================================================

prediction = model.predict(
    example
)[0]


print(
    "\n========== MODEL PREDICTION =========="
)

print(
    f"Predicted rent: ₹{prediction:,.2f}"
)


# ==================================================
# 13. GET BASE VALUE
# ==================================================

base_value = shap_result.base_values[0]

if hasattr(
    base_value,
    "__len__"
):
    base_value = base_value[0]

base_value = float(
    base_value
)


print(
    f"SHAP baseline: ₹{base_value:,.2f}"
)


# ==================================================
# 14. GET INDIVIDUAL SHAP VALUES
# ==================================================

raw_shap_values = (
    shap_result.values[0]
)


# ==================================================
# 15. CREATE RAW SHAP TABLE
# ==================================================

raw_shap_df = pd.DataFrame(
    {
        "transformed_feature":
            transformed_feature_names,

        "shap_value":
            raw_shap_values,
    }
)


print(
    "\n========== RAW SHAP VALUES =========="
)

print(
    raw_shap_df.to_string(
        index=False
    )
)


# ==================================================
# 16. GROUP SHAP VALUES INTO FRIENDLY FEATURES
# ==================================================

friendly_contributions = {
    "Locality": 0.0,
    "Size": 0.0,
    "BHK": 0.0,
    "Bathrooms": 0.0,
    "Furnishing status": 0.0,
    
}


for _, row in raw_shap_df.iterrows():

    feature_name = row[
        "transformed_feature"
    ]

    shap_value = float(
        row["shap_value"]
    )


    # Locality
    if feature_name.startswith(
        "categorical__locality_"
    ):

        friendly_contributions[
            "Locality"
        ] += shap_value


    # Furnishing
    elif feature_name.startswith(
        "categorical__furnishing_status_"
    ):

        friendly_contributions[
            "Furnishing status"
        ] += shap_value


    # Numeric features
    elif feature_name == (
        "numeric__size_sqft"
    ):

        friendly_contributions[
            "Size"
        ] += shap_value


    elif feature_name == (
        "numeric__bhk"
    ):

        friendly_contributions[
            "BHK"
        ] += shap_value


    elif feature_name == (
        "numeric__bathrooms"
    ):

        friendly_contributions[
            "Bathrooms"
        ] += shap_value



# ==================================================
# 17. CREATE FRIENDLY EXPLANATION TABLE
# ==================================================

explanation_df = pd.DataFrame(
    {
        "feature":
            list(
                friendly_contributions.keys()
            ),

        "shap_value":
            list(
                friendly_contributions.values()
            ),
    }
)


explanation_df[
    "absolute_shap_value"
] = (
    explanation_df[
        "shap_value"
    ].abs()
)


explanation_df = (
    explanation_df
    .sort_values(
        "absolute_shap_value",
        ascending=False
    )
    .reset_index(drop=True)
)


# ==================================================
# 18. SHOW FRIENDLY EXPLANATION
# ==================================================

print(
    "\n========== FRIENDLY SHAP CONTRIBUTIONS =========="
)

print(
    explanation_df.to_string(
        index=False
    )
)


# ==================================================
# 19. CHECK SHAP ADDITIVITY
# ==================================================

shap_total = (
    base_value
    + explanation_df[
        "shap_value"
    ].sum()
)


difference = abs(
    prediction
    - shap_total
)


print(
    "\n========== SHAP CHECK =========="
)

print(
    f"Prediction: ₹{prediction:,.2f}"
)

print(
    f"Baseline + SHAP values: ₹{shap_total:,.2f}"
)

print(
    f"Difference: ₹{difference:,.6f}"
)


# ==================================================
# 20. SAVE EXPLANATION TABLE
# ==================================================

explanation_file = (
    OUTPUT_DIR
    / "shap_example_contributions.csv"
)

explanation_df.to_csv(
    explanation_file,
    index=False
)


# ==================================================
# 21. CREATE FRIENDLY SHAP BAR CHART
# ==================================================

plot_df = (
    explanation_df
    .sort_values(
        "shap_value"
    )
)


plt.figure(
    figsize=(9, 5)
)


plt.barh(
    plot_df["feature"],
    plot_df["shap_value"]
)


plt.axvline(
    0
)


plt.title(
    "SHAP feature contributions for one rent prediction"
)


plt.xlabel(
    "Contribution to predicted rent (INR)"
)


plt.ylabel(
    "Feature"
)


plt.tight_layout()


plot_file = (
    OUTPUT_DIR
    / "07_shap_example.png"
)


plt.savefig(
    plot_file,
    dpi=150
)


plt.close()


# ==================================================
# 22. FINISHED
# ==================================================

print(
    "\nExplanation table saved to:"
)

print(
    explanation_file
)


print(
    "\nSHAP chart saved to:"
)

print(
    plot_file
)


print(
    "\n=================================================="
)

print(
    "SHAP EXPLAINABILITY COMPLETE"
)

print(
    "=================================================="
)