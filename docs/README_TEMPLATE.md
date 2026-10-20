# Bangalore Rental Price Predictor

## Project overview

A beginner-friendly machine learning web app that estimates a fair monthly rental range for apartments in selected Bangalore localities.

## Problem statement

Renters often receive an asking rent without knowing whether it is reasonable for the property's size, locality and basic characteristics. This project provides an estimated rental range and explains the main factors affecting the estimate.

## Scope

Localities:
- Whitefield
- Koramangala
- HSR Layout
- Indiranagar
- Electronic City
- Marathahalli

The application is based on a static training dataset and does not provide live property listings.

## User inputs

- Locality
- Size in square feet
- BHK
- Bathrooms
- Furnishing status

## Output

- Estimated fair rent range
- Point estimate
- SHAP-based feature contribution bars
- Plain-language explanation

## Tools

Python, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, SHAP, Streamlit, GitHub, Streamlit Community Cloud

## Methodology

1. Load raw rental data
2. Clean and standardize records
3. Filter to Bangalore and selected localities
4. Create modeling features
5. Perform exploratory data analysis
6. Train Linear Regression baseline
7. Train Random Forest Regressor
8. Compare RMSE and R²
9. Use SHAP for individual prediction explanations
10. Build and deploy Streamlit app

## Model results

Fill this section after training:

| Model | RMSE | R² |
|---|---:|---:|
| Linear Regression | TBD | TBD |
| Random Forest | TBD | TBD |

## Example prediction

Replace with a screenshot and real result after the app works.

## Important limitation

The displayed rent range is an approximate model-based range derived from observed validation errors. It is not a guaranteed market price, valuation, or formal confidence interval.

The data is static and may not represent current negotiated rents.

## Project links

GitHub: TBD

Live Streamlit app: TBD
