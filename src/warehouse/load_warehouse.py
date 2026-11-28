
import json

from pathlib import Path

from sqlalchemy import text

from src.database.connection import get_engine

from src.validation.validate_database import (
    validate_database
)


BASE_DIR = Path(__file__).resolve().parents[2]

WAREHOUSE_SQL_DIR = BASE_DIR / "sql" / "warehouse"


LOAD_FILES = [
    "05_load_date_dimension.sql",
    "06_load_dimensions.sql",
    "07_load_facts.sql"
]


DIMENSIONS = {
    "dim_customer": "customers",
    "dim_branch": "branches",
    "dim_account": "accounts",
    "dim_loan": "loans"
}


FACTS = {
    "fact_transactions": "transactions",
    "fact_payments": "payments",
    "fact_account_snapshot": "accounts",
    "fact_loan_snapshot": "loans"
}


def execute_sql_file(connection, filename):

    file_path = WAREHOUSE_SQL_DIR / filename

    if not file_path.exists():

        raise FileNotFoundError(
            f"SQL file not found: {file_path}"
        )

    sql_script = file_path.read_text(
        encoding="utf-8"
    )

    if not sql_script.strip():

        raise ValueError(
            f"SQL file is empty: {filename}"
        )

    connection.exec_driver_sql(sql_script)

    print(f"[EXECUTED] {filename}")


def get_table_count(connection, schema, table):

    return connection.execute(

        text(
            f"SELECT COUNT(*) "
            f"FROM {schema}.{table}"
        )

    ).scalar_one()


def get_latest_silver_load(connection):

    result = connection.execute(text("""

        SELECT
            load_id,
            source_silver_batch,
            total_records,
            table_counts

        FROM silver.load_history

        WHERE status = 'success'

        ORDER BY load_id DESC

        LIMIT 1

    """)).mappings().first()

    if result is None:

        raise RuntimeError(
            "No successful Silver database load found."
        )

    return result


def verify_silver_counts(connection, silver_load):

    expected_counts = silver_load["table_counts"]

    if isinstance(expected_counts, str):

        expected_counts = json.loads(expected_counts)

    actual_counts = {}

    for table in [
        "branches",
        "customers",
        "accounts",
        "transactions",
        "loans",
        "payments"
    ]:

        actual = get_table_count(
            connection,
            "silver",
            table
        )

        expected = expected_counts.get(table)

        if actual != expected:

            raise ValueError(
                f"Silver count mismatch for {table}: "
                f"expected {expected}, got {actual}"
            )

        actual_counts[table] = actual

    if sum(actual_counts.values()) != (
        silver_load["total_records"]
    ):

        raise ValueError(
            "Silver total record count mismatch."
        )

    return actual_counts


def load_warehouse():

    print("\nValidating Silver database...\n")

    validate_database()

    engine = get_engine()

    print("\nStarting warehouse loading pipeline...\n")

    try:

        with engine.begin() as connection:

            # Coordinate with the existing Silver loader
            # and analytics refresh process.

            connection.execute(text(
                "SELECT pg_advisory_xact_lock(42001)"
            ))

            silver_load = get_latest_silver_load(
                connection
            )

            source_counts = verify_silver_counts(
                connection,
                silver_load
            )

            print(
                "Source Silver batch:",
                silver_load["source_silver_batch"]
            )

            print(
                "Source Silver load ID:",
                silver_load["load_id"]
            )

            for filename in LOAD_FILES:

                execute_sql_file(
                    connection,
                    filename
                )

            dimension_counts = {}

            fact_counts = {}

            # Validate dimension coverage

            for target, source in DIMENSIONS.items():

                actual = get_table_count(
                    connection,
                    "warehouse",
                    target
                )

                expected = source_counts[source]

                # Type 1 dimensions can retain keys
                # from earlier source snapshots.

                if actual < expected:

                    raise ValueError(
                        f"Dimension count mismatch: "
                        f"{target}"
                    )

                dimension_counts[target] = actual

                print(
                    f"[LOADED] {target}: "
                    f"{actual} records"
                )

            dimension_counts["dim_date"] = (
                get_table_count(
                    connection,
                    "warehouse",
                    "dim_date"
                )
            )

            print(
                "[LOADED] dim_date:",
                dimension_counts["dim_date"],
                "records"
            )

            # Fact counts must match current Silver data.

            for target, source in FACTS.items():

                actual = get_table_count(
                    connection,
                    "warehouse",
                    target
                )

                expected = source_counts[source]

                if actual != expected:

                    raise ValueError(
                        f"Fact count mismatch for {target}: "
                        f"expected {expected}, got {actual}"
                    )

                fact_counts[target] = actual

                print(
                    f"[LOADED] {target}: "
                    f"{actual} records"
                )

            connection.execute(

                text("""

                    INSERT INTO warehouse.load_history (

                        source_silver_load_id,

                        source_silver_batch,

                        snapshot_date,

                        dimension_counts,

                        fact_counts,

                        status

                    )

                    VALUES (

                        :source_silver_load_id,

                        :source_silver_batch,

                        CURRENT_DATE,

                        CAST(:dimension_counts AS JSONB),

                        CAST(:fact_counts AS JSONB),

                        'success'

                    )

                """),

                {
                    "source_silver_load_id":
                        silver_load["load_id"],

                    "source_silver_batch":
                        silver_load["source_silver_batch"],

                    "dimension_counts":
                        json.dumps(dimension_counts),

                    "fact_counts":
                        json.dumps(fact_counts)
                }

            )

        print("\n--- Warehouse Loading Summary ---")

        print(
            "Total dimension records:",
            sum(dimension_counts.values())
        )

        print(
            "Total fact records:",
            sum(fact_counts.values())
        )

        print(
            "\nWarehouse loading committed successfully!"
        )

    except Exception:

        print(
            "\nWarehouse loading failed. "
            "Uncommitted changes were rolled back."
        )

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":

    load_warehouse()
