
import json
from pathlib import Path

from sqlalchemy import text

from src.database.connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[2]

SILVER_DIR = (
    BASE_DIR / "data" / "processed" / "silver"
)


PRIMARY_KEYS = {

    "branches": "branch_id",

    "customers": "customer_id",

    "accounts": "account_id",

    "transactions": "transaction_id",

    "loans": "loan_id",

    "payments": "payment_id"
}


RELATIONSHIPS = [

    (
        "customers", "home_branch_id",
        "branches", "branch_id"
    ),

    (
        "accounts", "customer_id",
        "customers", "customer_id"
    ),

    (
        "accounts", "branch_id",
        "branches", "branch_id"
    ),

    (
        "transactions", "account_id",
        "accounts", "account_id"
    ),

    (
        "transactions", "branch_id",
        "branches", "branch_id"
    ),

    (
        "loans", "customer_id",
        "customers", "customer_id"
    ),

    (
        "loans", "branch_id",
        "branches", "branch_id"
    ),

    (
        "payments", "loan_id",
        "loans", "loan_id"
    )
]


def check(condition, message, results):

    passed = bool(condition)

    results.append(passed)

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {message}")


def validate_database():

    engine = get_engine()

    results = []

    print("\nStarting database validation...\n")

    try:

        with engine.begin() as connection:

            # Prevent a cooperating loader from
            # changing the snapshot during validation.
            connection.execute(
                text(
                    "SELECT pg_advisory_xact_lock(42001)"
                )
            )

            latest_load = connection.execute(

                text(
                    """
                    SELECT *
                    FROM silver.load_history
                    ORDER BY load_id DESC
                    LIMIT 1
                    """
                )

            ).mappings().first()

            if latest_load is None:

                raise ValueError(
                    "No successful database loads found."
                )

            batch_name = latest_load[
                "source_silver_batch"
            ]

            manifest_path = (
                SILVER_DIR
                / batch_name
                / "manifest.json"
            )

            with open(manifest_path) as file:

                manifest = json.load(file)

            expected_counts = {

                entry["dataset"]: entry["output_rows"]

                for entry in manifest["datasets"]
            }

            actual_counts = {}

            print(
                f"Loaded Silver batch: {batch_name}\n"
            )

            # Record count and primary key validation.
            for name, primary_key in PRIMARY_KEYS.items():

                row = connection.execute(

                    text(
                        f"""
                        SELECT

                            COUNT(*) AS total,

                            COUNT({primary_key})
                                AS non_null,

                            COUNT(DISTINCT {primary_key})
                                AS unique_count

                        FROM silver.{name}
                        """
                    )

                ).mappings().one()

                actual_counts[name] = row["total"]

                check(

                    row["total"] == expected_counts[name],

                    f"{name}: record count",

                    results
                )

                check(

                    row["total"] == row["non_null"]
                    == row["unique_count"],

                    f"{name}: primary key integrity",

                    results
                )

            # Foreign key validation.
            for child, child_key, parent, parent_key in (
                RELATIONSHIPS
            ):

                orphan_count = connection.execute(

                    text(
                        f"""
                        SELECT COUNT(*)

                        FROM silver.{child} AS c

                        LEFT JOIN silver.{parent} AS p

                            ON c.{child_key}
                            = p.{parent_key}

                        WHERE p.{parent_key} IS NULL
                        """
                    )

                ).scalar_one()

                check(

                    orphan_count == 0,

                    f"{child}.{child_key} -> {parent}",

                    results
                )

            # Financial validation.
            rules = [

                (
                    "accounts",
                    "current_balance < 0"
                ),

                (
                    "transactions",
                    "amount <= 0"
                ),

                (
                    "loans",
                    "principal_amount <= 0"
                ),

                (
                    "payments",
                    "amount_paid <= 0"
                )
            ]

            for table, condition in rules:

                invalid_count = connection.execute(

                    text(
                        f"""
                        SELECT COUNT(*)

                        FROM silver.{table}

                        WHERE {condition}
                        """
                    )

                ).scalar_one()

                check(

                    invalid_count == 0,

                    f"{table}: financial business rule",

                    results
                )

            # Verify realized transaction amounts.
            invalid_transactions = connection.execute(

                text(
                    """
                    SELECT COUNT(*)

                    FROM silver.transactions

                    WHERE realized_amount !=

                        CASE

                            WHEN transaction_status
                                = 'Successful'

                            THEN signed_amount

                            ELSE 0

                        END
                    """
                )

            ).scalar_one()

            check(

                invalid_transactions == 0,

                "Realized transaction amounts",

                results
            )

            # Verify batch metadata.
            total_records = sum(
                actual_counts.values()
            )

            check(

                total_records
                == manifest["total_output_rows"],

                "Total database record reconciliation",

                results
            )

            check(

                total_records
                == latest_load["total_records"],

                "Load history total record count",

                results
            )

            check(

                actual_counts
                == latest_load["table_counts"],

                "Load history table counts",

                results
            )

            check(

                manifest["source_bronze_batch"]
                == latest_load["source_bronze_batch"],

                "Bronze-to-database lineage",

                results
            )

        print("\n--- Validation Summary ---")

        print(f"Total checks: {len(results)}")

        print(f"Passed: {sum(results)}")

        print(
            f"Failed: {len(results) - sum(results)}"
        )

        if not all(results):

            print("\nDatabase validation failed.")

            raise SystemExit(1)

        print(
            "\nDatabase validation successful!"
        )

    finally:

        engine.dispose()


if __name__ == "__main__":

    validate_database()
