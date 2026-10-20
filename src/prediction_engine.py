from pathlib import Path

import joblib
import pandas as pd
import shap


# ==================================================
# 1. PROJECT LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "final_model.joblib"
)

RANGE_FILE = (
    PROJECT_ROOT
    / "models"
    / "prediction_range_info.joblib"
)

MODEL_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_data.csv"
)


# ==================================================
# 2. MODEL INPUT COLUMNS
# ==================================================

FEATURE_COLUMNS = [
    "locality",
    "size_sqft",
    "bhk",
    "bathrooms",
    "furnishing_status",
   
]


# ==================================================
# 3. LOAD MODEL
# ==================================================

model = joblib.load(
    MODEL_FILE
)


# ==================================================
# 4. LOAD PREDICTION RANGE INFORMATION
# ==================================================

range_info = joblib.load(
    RANGE_FILE
)

LOWER_ERROR = range_info[
    "lower_error"
]

UPPER_ERROR = range_info[
    "upper_error"
]


# ==================================================
# 5. LOAD MODEL DATA
# ==================================================

model_data = pd.read_csv(
    MODEL_DATA_FILE
)

X_background = model_data[
    FEATURE_COLUMNS
].copy()


# ==================================================
# 6. GET PREPROCESSOR AND LINEAR MODEL
# ==================================================

preprocessor = model.named_steps[
    "preprocessor"
]

linear_regressor = model.named_steps[
    "model"
]


# ==================================================
# 7. CREATE SHAP BACKGROUND
# ==================================================

background = X_background.sample(
    n=min(30, len(X_background)),
    random_state=42
)

background_transformed = (
    preprocessor.transform(
        background
    )
)


# ==================================================
# 8. CREATE SHAP EXPLAINER
# ==================================================

explainer = shap.LinearExplainer(
    linear_regressor,
    background_transformed,
)


# ==================================================
# 9. PREDICT RENT
# ==================================================

def predict_rent(
    locality,
    size_sqft,
    bhk,
    bathrooms,
    furnishing_status,
):

   
    # ------------------------------------------------
    # Create one-row input table
    # ------------------------------------------------

    input_data = pd.DataFrame(
        [
            {
                "locality": locality,
                "size_sqft": size_sqft,
                "bhk": bhk,
                "bathrooms": bathrooms,
                "furnishing_status":
                    furnishing_status,
            }
        ]
    )


    # ------------------------------------------------
    # Predict rent
    # ------------------------------------------------

    prediction = model.predict(
        input_data
    )[0]


    # ------------------------------------------------
    # Create approximate rent range
    # ------------------------------------------------

    lower_rent = (
        prediction
        + LOWER_ERROR
    )

    upper_rent = (
        prediction
        + UPPER_ERROR
    )


    # Prevent a negative rent
    lower_rent = max(
        0,
        lower_rent
    )


    # ------------------------------------------------
    # SHAP input transformation
    # ------------------------------------------------

    transformed_input = (
        preprocessor.transform(
            input_data
        )
    )


    # ------------------------------------------------
    # Calculate SHAP values
    # ------------------------------------------------

    shap_result = explainer(
        transformed_input
    )


    # ------------------------------------------------
    # Get SHAP baseline
    # ------------------------------------------------

    base_value = (
        shap_result.base_values[0]
    )

    if hasattr(
        base_value,
        "__len__"
    ):
        base_value = base_value[0]

    base_value = float(
        base_value
    )


    # ------------------------------------------------
    # Get transformed feature names
    # ------------------------------------------------

    transformed_feature_names = (
        preprocessor
        .get_feature_names_out()
    )


    # ------------------------------------------------
    # Get SHAP values
    # ------------------------------------------------

    raw_shap_values = (
        shap_result.values[0]
    )


    # ------------------------------------------------
    # Friendly feature groups
    # ------------------------------------------------

    contribution_dict = {
        "Locality": 0.0,
        "Size": 0.0,
        "BHK": 0.0,
        "Bathrooms": 0.0,
        "Furnishing status": 0.0,
        
    }


    # ------------------------------------------------
    # Group transformed SHAP values
    # ------------------------------------------------

    for feature_name, shap_value in zip(
        transformed_feature_names,
        raw_shap_values,
    ):

        shap_value = float(
            shap_value
        )


        # Locality
        if feature_name.startswith(
            "categorical__locality_"
        ):

            contribution_dict[
                "Locality"
            ] += shap_value


        # Furnishing
        elif feature_name.startswith(
            "categorical__furnishing_status_"
        ):

            contribution_dict[
                "Furnishing status"
            ] += shap_value


        # Size
        elif feature_name == (
            "numeric__size_sqft"
        ):

            contribution_dict[
                "Size"
            ] += shap_value


        # BHK
        elif feature_name == (
            "numeric__bhk"
        ):

            contribution_dict[
                "BHK"
            ] += shap_value


        # Bathrooms
        elif feature_name == (
            "numeric__bathrooms"
        ):

            contribution_dict[
                "Bathrooms"
            ] += shap_value


        # BHK/bathroom ratio
        elif feature_name == (
            "numeric__bhk_bathroom_ratio"
        ):

            contribution_dict[
                "BHK/bathroom ratio"
            ] += shap_value


    # ------------------------------------------------
    # Create explanation DataFrame
    # ------------------------------------------------

    explanation = pd.DataFrame(
        {
            "feature":
                list(
                    contribution_dict.keys()
                ),

            "contribution":
                list(
                    contribution_dict.values()
                ),
        }
    )


    explanation[
        "absolute_contribution"
    ] = (
        explanation[
            "contribution"
        ].abs()
    )


    explanation = (
        explanation
        .sort_values(
            "absolute_contribution",
            ascending=False,
        )
        .reset_index(drop=True)
    )


    # ------------------------------------------------
    # Return results to the app
    # ------------------------------------------------

    return {
        "prediction": float(
            prediction
        ),

        "lower_rent": float(
            lower_rent
        ),

        "upper_rent": float(
            upper_rent
        ),

        "explanation":
            explanation,

        "base_value": float(
            base_value
        ),
    }