# Data dictionary

The exact raw column names will be confirmed after the dataset is downloaded.

Expected concepts from the rental dataset:

| Concept | Meaning | Final project name |
|---|---|---|
| BHK | Bedroom, hall and kitchen count | `bhk` |
| Rent | Monthly rental amount in INR | `rent` |
| Size | Property size in square feet | `size_sqft` |
| Area Locality | Locality name | `locality` |
| City | City name | `city` |
| Furnishing Status | Furnished / Semi-Furnished / Unfurnished | `furnishing_status` |
| Bathroom | Number of bathrooms | `bathrooms` |

Other raw columns may exist, such as floor, area type, tenant preference and point of contact.

For the first version:
- keep the raw columns untouched
- create a clean modeling table with only the features we actually use
- do not include contact details or other irrelevant fields

Target:
`rent`

Model inputs:
`locality`, `size_sqft`, `bhk`, `bathrooms`, `furnishing_status`

Quality checks:
- missing values
- duplicate rows
- impossible values
- extreme outliers
- inconsistent locality spellings
- inconsistent furnishing labels
- numeric columns stored as text
