from pathlib import Path
import pandas as pd

FILE_PATH = Path("data/processed/payments_clean.csv")

payments = pd.read_csv(FILE_PATH)

print(f"Total rows: {len(payments)}")
print(f"Duplicate rows: {payments.duplicated().sum()}")
print(f"Missing influencer names: {payments['influencer_name'].isna().sum()}")
print(f"Missing budgets: {payments['budget'].isna().sum()}")
print(f"Invalid budgets: {(payments['budget'] <= 0).sum()}")
print(f"Missing post dates: {payments['post_date'].isna().sum()}")

allowed_expense_types = {
    "influencer_fee",
    "shipping",
    "operations",
    "packaging"
}

invalid_expense_types = payments[
    ~payments["expense_type"].isin(allowed_expense_types)
]

print(f"Invalid expense types: {len(invalid_expense_types)}")

quality_errors = (
    payments.duplicated().sum()
    + payments["influencer_name"].isna().sum()
    + payments["budget"].isna().sum()
    + (payments["budget"] <= 0).sum()
    + len(invalid_expense_types)
)

if quality_errors > 0:
    raise ValueError(
        f"Data quality validation failed: {quality_errors} errors"
    )

print("Data quality validation passed.")