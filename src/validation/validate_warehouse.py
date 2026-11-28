
from sqlalchemy import text

from src.database.connection import get_engine


CHECKS = {

    "Customer dimension coverage": """
        SELECT NOT EXISTS (
            SELECT customer_id
            FROM silver.customers
            EXCEPT
            SELECT customer_id
            FROM warehouse.dim_customer
        )
    """,

    "Branch dimension coverage": """
        SELECT NOT EXISTS (
            SELECT branch_id
            FROM silver.branches
            EXCEPT
            SELECT branch_id
            FROM warehouse.dim_branch
        )
    """,

    "Account dimension coverage": """
        SELECT NOT EXISTS (
            SELECT account_id
            FROM silver.accounts
            EXCEPT
            SELECT account_id
            FROM warehouse.dim_account
        )
    """,

    "Loan dimension coverage": """
        SELECT NOT EXISTS (
            SELECT loan_id
            FROM silver.loans
            EXCEPT
            SELECT loan_id
            FROM warehouse.dim_loan
        )
    """,

    "Date dimension continuity": """
        SELECT
            COUNT(*) > 0
            AND COUNT(*) =
                MAX(full_date) - MIN(full_date) + 1
        FROM warehouse.dim_date
    """,

    "Date key correctness": """
        SELECT NOT EXISTS (
            SELECT 1
            FROM warehouse.dim_date
            WHERE date_key <>
                TO_CHAR(full_date, 'YYYYMMDD')::INTEGER
        )
    """,

    "Transaction fact count": """
        SELECT
            (SELECT COUNT(*)
             FROM warehouse.fact_transactions)
            =
            (SELECT COUNT(*)
             FROM silver.transactions)
    """,

    "Payment fact count": """
        SELECT
            (SELECT COUNT(*)
             FROM warehouse.fact_payments)
            =
            (SELECT COUNT(*)
             FROM silver.payments)
    """,

    "Account snapshot count": """
        SELECT
            (SELECT COUNT(*)
             FROM warehouse.fact_account_snapshot)
            =
            (SELECT COUNT(*)
             FROM silver.accounts)
    """,

    "Loan snapshot count": """
        SELECT
            (SELECT COUNT(*)
             FROM warehouse.fact_loan_snapshot)
            =
            (SELECT COUNT(*)
             FROM silver.loans)
    """,

    "Transaction grain uniqueness": """
        SELECT
            COUNT(*) = COUNT(DISTINCT transaction_id)
        FROM warehouse.fact_transactions
    """,

    "Payment grain uniqueness": """
        SELECT
            COUNT(*) = COUNT(DISTINCT payment_id)
        FROM warehouse.fact_payments
    """,

    "Transaction amount reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(amount), 0)
             FROM warehouse.fact_transactions)
            =
            (SELECT COALESCE(SUM(amount), 0)
             FROM silver.transactions)
    """,

    "Transaction net flow reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(realized_amount), 0)
             FROM warehouse.fact_transactions)
            =
            (SELECT COALESCE(SUM(realized_amount), 0)
             FROM silver.transactions)
    """,

    "Payment amount reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(realized_payment_amount), 0)
             FROM warehouse.fact_payments)
            =
            (SELECT COALESCE(
                SUM(realized_payment_amount), 0)
             FROM silver.payments)
    """,

    "Account balance reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(current_balance), 0)
             FROM warehouse.fact_account_snapshot)
            =
            (SELECT COALESCE(SUM(current_balance), 0)
             FROM silver.accounts)
    """,

    "Loan principal reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(principal_amount), 0)
             FROM warehouse.fact_loan_snapshot)
            =
            (SELECT COALESCE(SUM(principal_amount), 0)
             FROM silver.loans)
    """,

    "Loan payment aggregation reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(total_realized_payments), 0)
             FROM warehouse.fact_loan_snapshot)
            =
            (SELECT COALESCE(
                SUM(realized_payment_amount), 0)
             FROM silver.payments)
    """,

    "Transaction dimension mapping": """
        SELECT NOT EXISTS (

            SELECT 1

            FROM silver.transactions t

            JOIN silver.accounts a
                ON t.account_id = a.account_id

            LEFT JOIN warehouse.fact_transactions f
                ON t.transaction_id = f.transaction_id

            LEFT JOIN warehouse.dim_customer dc
                ON f.customer_key = dc.customer_key

            LEFT JOIN warehouse.dim_account da
                ON f.account_key = da.account_key

            LEFT JOIN warehouse.dim_branch db
                ON f.branch_key = db.branch_key

            LEFT JOIN warehouse.dim_date dd
                ON f.date_key = dd.date_key

            WHERE f.transaction_id IS NULL

            OR dc.customer_id
                IS DISTINCT FROM a.customer_id

            OR da.account_id
                IS DISTINCT FROM t.account_id

            OR db.branch_id
                IS DISTINCT FROM t.branch_id

            OR dd.full_date
                IS DISTINCT FROM t.transaction_date

        )
    """,

    "Silver to warehouse lineage": """
        SELECT COALESCE(

            (
                SELECT source_silver_load_id
                FROM warehouse.load_history
                ORDER BY load_id DESC
                LIMIT 1
            )

            =

            (
                SELECT load_id
                FROM silver.load_history
                WHERE status = 'success'
                ORDER BY load_id DESC
                LIMIT 1
            ),

            FALSE

        )
    """

}


def validate_warehouse():

    engine = get_engine()

    passed = 0

    failed = 0

    print("\nStarting warehouse validation...\n")

    try:

        with engine.begin() as connection:

            connection.execute(text(
                "SELECT pg_advisory_xact_lock(42001)"
            ))

            for name, query in CHECKS.items():

                result = connection.execute(
                    text(query)
                ).scalar_one()

                if result is True:

                    print(f"[PASS] {name}")

                    passed += 1

                else:

                    print(f"[FAIL] {name}")

                    failed += 1

        print(
            "\n--- Warehouse Validation Summary ---"
        )

        print(f"Total checks: {len(CHECKS)}")

        print(f"Passed: {passed}")

        print(f"Failed: {failed}")

        if failed > 0:

            raise SystemExit(1)

        print(
            "\nWarehouse validation successful!"
        )

    finally:

        engine.dispose()


if __name__ == "__main__":

    validate_warehouse()
