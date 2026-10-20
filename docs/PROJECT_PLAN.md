# Project plan

## 1. Business problem

A renter may be told that an apartment costs ₹X/month. They need a simple way to estimate whether that quoted rent is in a reasonable range for the apartment's size, locality and basic characteristics.

## 2. Solution

Build a machine learning model using historical rental data. A user enters:

- Locality
- Size in square feet
- BHK
- Number of bathrooms
- Furnishing status

The app returns:

1. Estimated fair monthly rent range
2. Approximate factors driving the estimate
3. A plain-language explanation

## 3. Why this is useful

A normal listing site may show asking prices. This project focuses on explaining the estimate for one apartment.

## 4. Project scope

Only these six Bangalore localities are included:

- Whitefield
- Koramangala
- HSR Layout
- Indiranagar
- Electronic City
- Marathahalli

The training data is static. The model will not fetch live listings.

## 5. Machine learning plan

Target:
- monthly rent in INR

Candidate features:
- locality
- size_sqft
- bhk
- bathrooms
- furnishing_status

Potential engineered features:
- rent_per_sqft for analysis only
- bhk_bathroom_ratio
- locality_group

IMPORTANT:
Do NOT use `rent_per_sqft` as an input feature for predicting rent because it is derived from the target rent and would cause target leakage.

Models:
- Linear Regression — baseline
- Random Forest Regressor — non-linear model

Metrics:
- RMSE
- R²

Model selection:
- Compare validation performance.
- Evaluate the selected model on a separate test set.

## 6. Rent range design

A tree model produces a point prediction. For this beginner project, the app will turn the point prediction into an approximate range using residuals observed on a validation set.

Example idea:

predicted rent = ₹30,000
validation residual range = roughly ±₹2,000

app range = ₹28,000–₹32,000

This is an approximate error-based range, not a guaranteed market quote or a formal statistical confidence interval. The README must say this clearly.

## 7. Explainability

Use SHAP with the final Random Forest model.

For an individual apartment:
- positive SHAP value = pushes the prediction upward
- negative SHAP value = pushes the prediction downward
- larger absolute value = larger contribution

The UI will translate this into simple bars and plain language.

## 8. App design

Single screen.
No navigation menu.

Top:
- title
- one-sentence explanation

Input card:
- locality dropdown
- sqft number input
- BHK number input
- bathroom number input
- furnishing dropdown
- Predict rent button

Result card:
- large rent range
- smaller point estimate
- horizontal "why this estimate?" bars

Footer:
- dataset last-updated date
- simple disclaimer
