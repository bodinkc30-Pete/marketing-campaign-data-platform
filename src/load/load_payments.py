from pathlib import Path
import sqlite3
import pandas as pd
DATABASE_FILE = Path("database/marketing_analytics.db")
SCHEMA_FILE = Path("schema/create_tables.sql")
PAYMENTS_FILE = Path("data/processed/payments_clean.csv")
DATABASE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)
schema_sql = SCHEMA_FILE.read_text(
    encoding="utf-8"
)
payments = pd.read_csv(PAYMENTS_FILE)
payments["post_date"] = payments["post_date"].where(
    payments["post_date"].notna(),
    None
)
with sqlite3.connect(DATABASE_FILE) as connection:
    connection.execute("DROP TABLE IF EXISTS payments")
    connection.executescript(schema_sql)
    payments.to_sql(
        "payments",
        connection,
        if_exists="append",
        index=False
    )
    row_count = connection.execute(
        "SELECT COUNT(*) FROM payments"
    ).fetchone()[0]
print(f"Database: {DATABASE_FILE}")
print(f"Loaded rows: {row_count}")