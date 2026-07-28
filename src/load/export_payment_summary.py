from pathlib import Path
import sqlite3
import pandas as pd

DATABASE_FILE = Path("database/marketing_analytics.db")
OUTPUT_FILE = Path("reports/payment_summary.csv")

query = """
SELECT
    expense_type,
    COUNT(*) AS expense_count,
    SUM(budget) AS total_budget,
    ROUND(AVG(budget), 2) AS average_budget
FROM payments
GROUP BY expense_type
ORDER BY total_budget DESC
"""

with sqlite3.connect(DATABASE_FILE) as connection:
    summary = pd.read_sql_query(query, connection)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

summary.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Report saved: {OUTPUT_FILE}")
print(summary.to_string(index=False))