
from sqlalchemy import text

from src.database.connection import get_engine


CHECKS = {

    "Customer 360 record count": """
        SELECT
            (SELECT COUNT(*)
             FROM analytics.v_customer_360)
            =
            (SELECT COUNT(*)
             FROM silver.customers)
    """,

    "Customer 360 unique grain": """
        SELECT COUNT(*) = COUNT(DISTINCT customer_id)
        FROM analytics.v_customer_360
    """,

    "Branch performance record count": """
        SELECT
            (SELECT COUNT(*)
             FROM analytics.v_branch_performance)
            =
            (SELECT COUNT(*)
             FROM silver.branches)
    """,

    "Branch performance unique grain": """
        SELECT COUNT(*) = COUNT(DISTINCT branch_id)
        FROM analytics.v_branch_performance
    """,

    "Customer account count reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(total_accounts), 0)
             FROM analytics.v_customer_360)
            =
            (SELECT COUNT(*)
             FROM silver.accounts)
    """,

    "Customer balance reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(total_account_balance), 0)
             FROM analytics.v_customer_360)
            =
            (SELECT COALESCE(
                SUM(current_balance), 0)
             FROM silver.accounts)
    """,

    "Branch balance reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(total_account_balance), 0)
             FROM analytics.v_branch_performance)
            =
            (SELECT COALESCE(
                SUM(current_balance), 0)
             FROM silver.accounts)
    """,

    "Daily transaction count reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(total_transactions), 0)
             FROM analytics.v_daily_transactions)
            =
            (SELECT COUNT(*)
             FROM silver.transactions)
    """,

    "Daily transaction status reconciliation": """
        SELECT NOT EXISTS (
            SELECT 1
            FROM analytics.v_daily_transactions
            WHERE total_transactions <>
                successful_transactions
                + failed_transactions
                + pending_transactions
        )
    """,

    "Net transaction flow reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(net_transaction_flow), 0)
             FROM analytics.v_daily_transactions)
            =
            (SELECT COALESCE(
                SUM(realized_amount), 0)
             FROM silver.transactions)
    """,

    "Loan count reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(total_loans), 0)
             FROM analytics.v_loan_portfolio)
            =
            (SELECT COUNT(*)
             FROM silver.loans)
    """,

    "Loan principal reconciliation": """
        SELECT
            (SELECT COALESCE(
                SUM(total_loan_principal), 0)
             FROM analytics.v_loan_portfolio)
            =
            (SELECT COALESCE(
                SUM(principal_amount), 0)
             FROM silver.loans)
    """,

    "Account portfolio reconciliation": """
        SELECT
            (SELECT COALESCE(SUM(total_accounts), 0)
             FROM analytics.v_account_portfolio)
            =
            (SELECT COUNT(*)
             FROM silver.accounts)
    """,

    "Materialized branch view consistency": """
        SELECT NOT EXISTS (

            (
                SELECT *
                FROM analytics.v_branch_performance

                EXCEPT ALL

                SELECT *
                FROM analytics.mv_branch_performance
            )

            UNION ALL

            (
                SELECT *
                FROM analytics.mv_branch_performance

                EXCEPT ALL

                SELECT *
                FROM analytics.v_branch_performance
            )
        )
    """,

    "Materialized customer view consistency": """
        SELECT NOT EXISTS (

            (
                SELECT *
                FROM analytics.v_customer_360

                EXCEPT ALL

                SELECT *
                FROM analytics.mv_customer_360
            )

            UNION ALL

            (
                SELECT *
                FROM analytics.mv_customer_360

                EXCEPT ALL

                SELECT *
                FROM analytics.v_customer_360
            )
        )
    """
}


def validate_analytics():

    engine = get_engine()

    passed = 0
    failed = 0

    print("\nStarting analytics validation...\n")

    try:

        with engine.begin() as connection:

            connection.execute(
                text(
                    "SELECT pg_advisory_xact_lock(42001)"
                )
            )

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

        print("\n--- Analytics Validation Summary ---")

        print(f"Total checks: {len(CHECKS)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed > 0:

            raise SystemExit(1)

        print(
            "\nAnalytics validation successful!"
        )

    finally:

        engine.dispose()


if __name__ == "__main__":

    validate_analytics()
