from pathlib import Path
import pandas as pd
INPUT_FILE = Path("data/raw/pawchoice/pawchoice_payments.xlsx")
CLEAN_FILE = Path("data/processed/payments_clean.csv")
REJECTED_FILE = Path("data/staging/payments_rejected.csv")
dataframe = pd.read_excel(
    INPUT_FILE,
    sheet_name="Allทำจ่าย",
    header=1
)
payments = dataframe.iloc[:, [1, 2, 3, 5, 6]].copy()
payments.columns = [
    "influencer_name",
    "budget",
    "post_date",
    "payment_round",
    "payment_status"
]
payments["influencer_name"] = (
    payments["influencer_name"]
    .astype("string")
    .str.strip()
)
payments["budget"] = pd.to_numeric(
    payments["budget"],
    errors="coerce"
)
payments["post_date"] = pd.to_datetime(
    payments["post_date"],
    errors="coerce"
)
invalid_names = [
    "Influencer",
    "จำนวน",
    "จำนวนไม่ตรง",
    "จำนวนถูกต้อง",
    "เงินทั้งหมด"
]
name_has_letter = payments["influencer_name"].str.contains(
    r"[A-Za-zก-๙]",
    regex=True,
    na=False
)
valid_mask = (
    payments["influencer_name"].notna()
    & name_has_letter
    & ~payments["influencer_name"].isin(invalid_names)
    & payments["budget"].notna()
    & (payments["budget"] > 0)
)
clean_payments = payments[valid_mask].copy()
clean_payments = clean_payments.drop_duplicates()
clean_payments["expense_type"] = "influencer_fee"
shipping_mask = clean_payments["influencer_name"].str.contains(
    r"ส่ง\s*ของ|ค่า\s*ส่ง",
    regex=True,
    na=False
)
clean_payments.loc[
    shipping_mask,
    "expense_type"
] = "shipping"
packaging_mask = clean_payments["influencer_name"].str.contains(
    r"ค่ากล่อง|กล่อง",
    regex=True,
    na=False
)

clean_payments.loc[
    packaging_mask,
    "expense_type"
] = "packaging"
operations_mask = clean_payments["influencer_name"].str.contains(
    r"ค่าก๋วยเตี๋ยว|เปิดห้อง",
    regex=True,
    na=False
)

clean_payments.loc[
    operations_mask,
    "expense_type"
] = "operations"
rejected_payments = payments[~valid_mask].copy()
clean_payments["post_date"] = (
    clean_payments["post_date"]
    .dt.strftime("%Y-%m-%d")
)
CLEAN_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)
REJECTED_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)
clean_payments.to_csv(
    CLEAN_FILE,
    index=False,
    encoding="utf-8-sig"
)
rejected_payments.to_csv(
    REJECTED_FILE,
    index=False,
    encoding="utf-8-sig"
)
print(f"Clean file: {CLEAN_FILE}")
print(f"Clean rows: {len(clean_payments)}")
print(f"Rejected file: {REJECTED_FILE}")
print(f"Rejected rows: {len(rejected_payments)}")
