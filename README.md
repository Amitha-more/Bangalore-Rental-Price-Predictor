# Bangalore Rental Price Predictor

A Streamlit app that helps renters assess an apartment's asking rent in six Bangalore localities. Enter the locality, size, BHK, number of bathrooms, and furnishing status to get a historical-data-based rent estimate, an approximate range, an explanation of the estimate, and a comparison with saved asking-rent listings.

## Features

- Estimates monthly rent in INR from locality, apartment size, BHK, bathrooms, and furnishing status.
- Shows an approximate rent range based on prediction errors observed during cross-validation.
- Uses SHAP to show how apartment features contribute to the model estimate.
- Compares the estimate with a saved snapshot of similar asking-rent listings, including median and quartiles when comparables are available.
- Supports Whitefield, Koramangala, HSR Layout, Indiranagar, Electronic City, and Marathahalli.

## Run the app

Use Python 3.10 or newer. From the project root, create and activate a virtual environment, install dependencies, and start Streamlit:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then install and run:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. Stop it with `Ctrl+C` in the terminal.

## Data and model files

The app expects these files at the listed paths:

- `models/final_model.joblib` - trained scikit-learn prediction pipeline.
- `models/prediction_range_info.joblib` - residual percentiles used for the approximate range.
- `data/processed/model_data.csv` - modeling data used to create the SHAP background sample.
- `data/processed/all_live_clean_standardized.csv` - saved comparable listing snapshot used for the market reference.

Data CSVs and model binaries are excluded from Git by `.gitignore`. If you clone this repository, provide these files locally before running the app. The project includes data preparation and model training scripts under `src/`; see [START_HERE.md](START_HERE.md), [the project plan](docs/PROJECT_PLAN.md), and [the data dictionary](docs/DATA_DICTIONARY.md) for the workflow and expected fields. The raw training dataset belongs in `data/raw/`.

## How it works

The training workflow prepares rental records, limits the modeling data to the six supported localities, compares Linear Regression with Random Forest, and evaluates candidates using five-fold cross-validation and a held-out test set. Features include locality, size in square feet, BHK, bathrooms, and furnishing status. The current saved model is a scikit-learn pipeline; the prediction engine uses its preprocessor and SHAP to group feature contributions into a readable explanation.

For the market reference, the app searches the saved listing snapshot for the same locality and BHK and a similar apartment size. It uses listings with the requested furnishing status when enough matches exist, otherwise it falls back to all furnishing categories. Listing counts and sample-quality labels are shown with the comparison.

## Recorded model results

The checked-in comparison report (`models/model_comparison.csv`) records these held-out test metrics:

| Model | RMSE (INR) | R-squared |
| --- | ---: | ---: |
| Linear Regression | 11,234.91 | 0.4834 |
| Random Forest | 11,779.03 | 0.4321 |

The cross-validation report records mean RMSE of INR 12,350.95 for Linear Regression and INR 17,088.96 for Random Forest. The training script selects the model with the lowest mean cross-validation RMSE, so Linear Regression is selected in the current run. These scores describe the available dataset and split; they do not guarantee accuracy for every property or current market conditions.

## Project structure

```text
|-- app.py                         # Streamlit user interface
|-- src/
|   |-- prediction_engine.py        # Model prediction and SHAP explanation
|   |-- unified_prediction_engine.py # Combines model and market comparison
|   |-- 04_train_models.py          # Model training and evaluation
|   `-- ...                         # Data preparation and analysis scripts
|-- data/
|   |-- raw/                        # Raw training data
|   |-- processed/                  # Cleaned/modeling data and market snapshot
|   `-- live_raw/                   # Collected listing source files
|-- models/                         # Saved model and evaluation reports
|-- reports/figures/                # EDA charts and explanation examples
|-- docs/                           # Project plan, checklist, and data dictionary
`-- requirements.txt
```

## Limitations

- The estimated rent range is an approximate range derived from historical model residuals. It is not a formal confidence interval, guaranteed fair price, or property valuation.
- The model is trained on static historical rental data and covers only the six listed Bangalore localities.
- The market comparison uses a saved snapshot of collected asking prices. It is not fetched automatically in real time, and asking prices may differ from negotiated or completed rents.
- Comparable listing counts can be small. Treat the market statistics as a rough reference when the app labels sample quality as limited.

## Technology

Python, Pandas, NumPy, scikit-learn, SHAP, Streamlit, Matplotlib, and Seaborn.
