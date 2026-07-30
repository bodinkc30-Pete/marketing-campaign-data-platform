import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "marketing_analytics.db"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "reports"
    / "portfolio_outputs"
)


EXPORT_QUERIES = {
    "sample_masked_payment_records.csv": """
        WITH masked_payments AS (
            SELECT
                printf(
                    'influencer_%03d',
                    DENSE_RANK() OVER (
                        ORDER BY influencer_name
                    )
                ) AS influencer_alias,
                budget,
                expense_type,
                post_date,
                payment_round,
                COALESCE(
                    NULLIF(
                        TRIM(payment_status),
                        ''
                    ),
                    'ไม่ระบุสถานะ'
                ) AS payment_status
            FROM payments
        )
        SELECT
            influencer_alias,
            ROUND(
                budget,
                2
            ) AS budget,
            expense_type,
            post_date,
            payment_round,
            payment_status
        FROM masked_payments
        ORDER BY
    CASE
        WHEN post_date IS NULL
             OR TRIM(post_date) = ''
        THEN 1
        ELSE 0
    END,
    post_date,
    influencer_alias
LIMIT 20;
    """,

    "sample_payment_status_summary.csv": """
        SELECT
            COALESCE(
                NULLIF(
                    TRIM(payment_status),
                    ''
                ),
                'ไม่ระบุสถานะ'
            ) AS payment_status,
            COUNT(*) AS payment_count,
            ROUND(
                SUM(budget),
                2
            ) AS total_budget,
            ROUND(
                AVG(budget),
                2
            ) AS average_budget,
            ROUND(
                MIN(budget),
                2
            ) AS minimum_budget,
            ROUND(
                MAX(budget),
                2
            ) AS maximum_budget
        FROM payments
        GROUP BY
            COALESCE(
                NULLIF(
                    TRIM(payment_status),
                    ''
                ),
                'ไม่ระบุสถานะ'
            )
        ORDER BY total_budget DESC;
    """,

    "sample_expense_type_summary.csv": """
        SELECT
            expense_type,
            COUNT(*) AS expense_count,
            ROUND(
                SUM(budget),
                2
            ) AS total_budget,
            ROUND(
                AVG(budget),
                2
            ) AS average_budget,
            ROUND(
                100.0
                * SUM(budget)
                / (
                    SELECT SUM(budget)
                    FROM payments
                ),
                2
            ) AS budget_percentage
        FROM payments
        GROUP BY expense_type
        ORDER BY total_budget DESC;
    """,

    "sample_payment_round_summary.csv": """
        SELECT
            COALESCE(
                NULLIF(
                    TRIM(payment_round),
                    ''
                ),
                'ไม่ระบุรอบจ่าย'
            ) AS payment_round,
            COUNT(*) AS payment_count,
            ROUND(
                SUM(budget),
                2
            ) AS total_budget,
            ROUND(
                SUM(
                    CASE
                        WHEN payment_status = 'ทำจ่ายแล้ว'
                        THEN budget
                        ELSE 0
                    END
                ),
                2
            ) AS paid_budget,
            ROUND(
                SUM(
                    CASE
                        WHEN payment_status = 'ยังไม่ทำจ่าย'
                        THEN budget
                        ELSE 0
                    END
                ),
                2
            ) AS unpaid_budget,
            ROUND(
                SUM(
                    CASE
                        WHEN payment_status IS NULL
                             OR TRIM(payment_status) = ''
                        THEN budget
                        ELSE 0
                    END
                ),
                2
            ) AS unspecified_status_budget
        FROM payments
        GROUP BY
            COALESCE(
                NULLIF(
                    TRIM(payment_round),
                    ''
                ),
                'ไม่ระบุรอบจ่าย'
            )
        ORDER BY payment_round;
    """,

    "sample_monthly_payment_summary.csv": """
        SELECT
            SUBSTR(
                post_date,
                1,
                7
            ) AS post_month,
            COUNT(*) AS payment_count,
            ROUND(
                SUM(budget),
                2
            ) AS total_budget,
            ROUND(
                AVG(budget),
                2
            ) AS average_budget,
            ROUND(
                SUM(
                    CASE
                        WHEN payment_status = 'ทำจ่ายแล้ว'
                        THEN budget
                        ELSE 0
                    END
                ),
                2
            ) AS paid_budget,
            ROUND(
                SUM(
                    CASE
                        WHEN payment_status = 'ยังไม่ทำจ่าย'
                        THEN budget
                        ELSE 0
                    END
                ),
                2
            ) AS unpaid_budget
        FROM payments
        WHERE post_date IS NOT NULL
          AND TRIM(post_date) <> ''
        GROUP BY
            SUBSTR(
                post_date,
                1,
                7
            )
        ORDER BY post_month;
    """,

    "sample_data_quality_summary.csv": """
        SELECT
            COUNT(*) AS total_records,

            SUM(
                CASE
                    WHEN influencer_name IS NULL
                         OR TRIM(influencer_name) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS missing_influencer_records,

            SUM(
                CASE
                    WHEN budget IS NULL
                         OR budget < 0
                    THEN 1
                    ELSE 0
                END
            ) AS invalid_budget_records,

            SUM(
                CASE
                    WHEN expense_type IS NULL
                         OR TRIM(expense_type) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS missing_expense_type_records,

            SUM(
                CASE
                    WHEN post_date IS NULL
                         OR TRIM(post_date) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS missing_post_date_records,

            SUM(
                CASE
                    WHEN post_date IS NOT NULL
                         AND TRIM(post_date) <> ''
                         AND DATE(post_date) IS NULL
                    THEN 1
                    ELSE 0
                END
            ) AS invalid_post_date_records,

            SUM(
                CASE
                    WHEN payment_status IS NULL
                         OR TRIM(payment_status) = ''
                    THEN 1
                    ELSE 0
                END
            ) AS missing_payment_status_records,

            SUM(
                CASE
                    WHEN payment_status IS NOT NULL
                         AND TRIM(payment_status) <> ''
                         AND payment_status NOT IN (
                             'ทำจ่ายแล้ว',
                             'ยังไม่ทำจ่าย'
                         )
                    THEN 1
                    ELSE 0
                END
            ) AS unexpected_payment_status_records,

            COUNT(*)
            - COUNT(DISTINCT payment_id)
                AS duplicate_payment_id_records
        FROM payments;
    """
}


def export_query_to_csv(
    connection: sqlite3.Connection,
    output_file: Path,
    query: str
) -> int:
    cursor = connection.execute(query)

    column_names = [
        description[0]
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    with output_file.open(
        mode="w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(column_names)
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"ไม่พบฐานข้อมูล: {DATABASE_PATH}"
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:
        total_exported_rows = 0

        print(
            f"[INFO] Database: "
            f"{DATABASE_PATH}"
        )

        print(
            f"[INFO] Output directory: "
            f"{OUTPUT_DIRECTORY}"
        )

        print("-" * 70)

        for file_name, query in EXPORT_QUERIES.items():
            output_file = (
                OUTPUT_DIRECTORY
                / file_name
            )

            exported_rows = export_query_to_csv(
                connection=connection,
                output_file=output_file,
                query=query
            )

            total_exported_rows += exported_rows

            print(
                f"[SUCCESS] สร้าง "
                f"{file_name}: "
                f"{exported_rows} แถว"
            )

        print("-" * 70)

        print(
            "[SUCCESS] สร้าง Portfolio Outputs "
            "ครบทุกไฟล์แล้ว"
        )

        print(
            f"[INFO] จำนวนไฟล์: "
            f"{len(EXPORT_QUERIES)}"
        )

        print(
            f"[INFO] จำนวนแถวรวม: "
            f"{total_exported_rows}"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()