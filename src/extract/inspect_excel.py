from pathlib import Path
import pandas as pd

FILE_PATH = Path("data/raw/pawchoice/pawchoice_payments.xlsx")
SHEET_NAME = "Allทำจ่าย"

dataframe = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME,
    header=1
)

print("Columns:")
for column in dataframe.columns:
    print(column)

print("\nFirst 10 rows:")
print(dataframe.head(10).to_string())