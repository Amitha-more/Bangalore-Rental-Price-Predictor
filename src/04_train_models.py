from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import (
    KFold,
    cross_val_predict,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ==================================================
# 1. FILE LOCATIONS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_data.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# 2. LOAD DATA
# ==================================================

df = pd.read_csv(
    MODEL_DATA_FILE
)

print("==================================================")
print("MODEL TRAINING AND VALIDATION")
print("==================================================")

print("\nDataset shape:")
print(df.shape)


# ==================================================
# 3. FEATURES AND TARGET
# ==================================================

X = df[
    [
        "locality",
        "size_sqft",
        "bhk",
        "bathrooms",
        "furnishing_status",
    ]
]

y = df["rent"]


# ==================================================
# 4. HOLD OUT FINAL TEST SET
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\n========== DATA SPLIT ==========")

print(
    "Training rows:",
    len(X_train)
)

print(
    "Final test rows:",
    len(X_test)
)


# ==================================================
# 5. FEATURE TYPES
# ==================================================

categorical_features = [
    "locality",
    "furnishing_status",
]

numeric_features = [
    "size_sqft",
    "bhk",
    "bathrooms",
]


# ==================================================
# 6. PREPROCESSING
# ==================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                drop="first",
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


# ==================================================
# 7. CREATE MODELS
# ==================================================

linear_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            LinearRegression()
        ),
    ]
)


random_forest_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                min_samples_leaf=2,
            )
        ),
    ]
)


models = {
    "Linear Regression": linear_model,
    "Random Forest": random_forest_model,
}


# ==================================================
# 8. 5-FOLD CROSS-VALIDATION
# ==================================================

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


print("\n========== 5-FOLD CROSS-VALIDATION ==========")

cv_results = []

oof_predictions = {}


for model_name, model in models.items():

    # ----------------------------------------------
    # Cross-validation RMSE
    # ----------------------------------------------

    negative_rmse_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="neg_root_mean_squared_error",
    )

    rmse_scores = -negative_rmse_scores


    # ----------------------------------------------
    # Cross-validation R²
    # ----------------------------------------------

    r2_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="r2",
    )


    # ----------------------------------------------
    # Out-of-fold predictions
    # ----------------------------------------------

    oof_prediction_values = cross_val_predict(
        model,
        X_train,
        y_train,
        cv=cv,
    )

    oof_predictions[model_name] = (
        oof_prediction_values
    )


    # ----------------------------------------------
    # Print results
    # ----------------------------------------------

    print(f"\n{model_name}")

    print(
        f"Average CV RMSE: "
        f"₹{rmse_scores.mean():,.2f}"
    )

    print(
        f"CV RMSE standard deviation: "
        f"₹{rmse_scores.std():,.2f}"
    )

    print(
        f"Average CV R²: "
        f"{r2_scores.mean():.4f}"
    )


    cv_results.append(
        {
            "Model": model_name,
            "CV_RMSE_Mean": rmse_scores.mean(),
            "CV_RMSE_STD": rmse_scores.std(),
            "CV_R2_Mean": r2_scores.mean(),
        }
    )


cv_results_df = pd.DataFrame(
    cv_results
)


# ==================================================
# 9. SELECT MODEL USING CROSS-VALIDATION
# ==================================================

best_model_name = (
    cv_results_df
    .sort_values("CV_RMSE_Mean")
    .iloc[0]["Model"]
)


print("\n========== MODEL SELECTED ==========")

print(
    "Selected using lowest average CV RMSE:",
    best_model_name
)


# ==================================================
# 10. CALCULATE OOF RESIDUAL RANGE
# ==================================================

selected_oof_predictions = (
    oof_predictions[
        best_model_name
    ]
)

oof_residuals = (
    y_train.to_numpy()
    - selected_oof_predictions
)


lower_error = np.percentile(
    oof_residuals,
    10
)

upper_error = np.percentile(
    oof_residuals,
    90
)


print("\n========== APPROXIMATE ERROR RANGE ==========")

print(
    f"10th percentile residual: "
    f"₹{lower_error:,.2f}"
)

print(
    f"90th percentile residual: "
    f"₹{upper_error:,.2f}"
)


# ==================================================
# 11. TRAIN SELECTED MODEL ON TRAINING DATA ONLY
# ==================================================

final_model = models[
    best_model_name
]


final_model.fit(
    X_train,
    y_train
)


# ==================================================
# 12. FINAL TEST EVALUATION
# ==================================================

# IMPORTANT:
# This happens BEFORE retraining on all 93 rows.

test_predictions = (
    final_model.predict(
        X_test
    )
)


test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        test_predictions
    )
)


test_r2 = r2_score(
    y_test,
    test_predictions
)


print("\n========== FINAL TEST RESULTS ==========")

print(
    f"Model: {best_model_name}"
)

print(
    f"Test RMSE: "
    f"₹{test_rmse:,.2f}"
)

print(
    f"Test R²: "
    f"{test_r2:.4f}"
)


# ==================================================
# 13. RETRAIN ON ALL 93 ROWS FOR DEPLOYMENT
# ==================================================

print(
    "\nRetraining selected model "
    "on all 93 observations..."
)


deployment_model = models[
    best_model_name
]


deployment_model.fit(
    X,
    y
)


# ==================================================
# 14. SAVE RESULTS
# ==================================================

cv_results_df.to_csv(
    MODEL_DIR
    / "cross_validation_results.csv",
    index=False
)


# ==================================================
# 15. SAVE FINAL DEPLOYMENT MODEL
# ==================================================

joblib.dump(
    deployment_model,
    MODEL_DIR
    / "final_model.joblib"
)


# ==================================================
# 16. SAVE PREDICTION RANGE INFORMATION
# ==================================================

range_info = {
    "lower_error": float(
        lower_error
    ),
    "upper_error": float(
        upper_error
    ),
}


joblib.dump(
    range_info,
    MODEL_DIR
    / "prediction_range_info.joblib"
)


# ==================================================
# 17. FINISHED
# ==================================================

print(
    "\nFinal deployment model saved to:"
)

print(
    MODEL_DIR
    / "final_model.joblib"
)


print(
    "\nPrediction range information saved to:"
)

print(
    MODEL_DIR
    / "prediction_range_info.joblib"
)


print(
    "\n=================================================="
)

print(
    "MODEL TRAINING COMPLETE"
)

print(
    "=================================================="
)