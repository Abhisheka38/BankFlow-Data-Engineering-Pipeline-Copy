from src.validation.validate_silver import (
    validate_silver
)
from src.database.connection import get_engine
from sqlalchemy import text, Numeric
import pandas as pd
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json
import hashlib
SQL_DTYPES = {
    "branches": {},

    "customers": {},

    "accounts": {
        "current_balance": Numeric(18, 2)
    },

    "transactions": {
        "amount": Numeric(18, 2),
        "signed_amount": Numeric(18, 2),
        "realized_amount": Numeric(18, 2)
    },

    "loans": {
        "principal_amount": Numeric(18, 2),
        "annual_interest_rate": Numeric(5, 2),
        "annual_interest_rate_decimal": Numeric(7, 6)
    },

    "payments": {
        "amount_paid": Numeric(18, 2),
        "realized_payment_amount": Numeric(18, 2)
    }
}


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

SILVER_DIR = (
    BASE_DIR / "data" / "processed" / "silver"
)

DATASETS = [

    "branches",

    "customers",

    "accounts",

    "transactions",

    "loans",

    "payments"
]


# Financial columns and decimal precision

DECIMAL_COLUMNS = {

    "accounts": {
        "current_balance": "0.01"
    },

    "transactions": {
        "amount": "0.01",
        "signed_amount": "0.01",
        "realized_amount": "0.01"
    },

    "loans": {
        "principal_amount": "0.01",
        "annual_interest_rate": "0.01",
        "annual_interest_rate_decimal": "0.000001"
    },

    "payments": {
        "amount_paid": "0.01",
        "realized_payment_amount": "0.01"
    }
}


DATE_COLUMNS = {

    "branches": [
        "opened_date"
    ],

    "customers": [
        "date_of_birth",
        "registration_date"
    ],

    "accounts": [
        "opened_date"
    ],

    "transactions": [
        "transaction_date"
    ],

    "loans": [
        "loan_date",
        "maturity_date"
    ],

    "payments": [
        "payment_date"
    ]
}


# --------------------------------------------------
# 2. FIND LATEST SILVER BATCH
# --------------------------------------------------

def get_latest_silver_batch():

    batches = sorted(

        path
        for path in SILVER_DIR.glob("run_id=*")
        if path.is_dir()
    )

    if not batches:

        raise FileNotFoundError(
            "No Silver batches found."
        )

    return batches[-1]


# --------------------------------------------------
# 3. CONVERT FINANCIAL VALUES
# --------------------------------------------------

def to_decimal(value, precision):

    if pd.isna(value):

        return None

    return Decimal(str(value)).quantize(

        Decimal(precision),

        rounding=ROUND_HALF_UP
    )


# --------------------------------------------------
# 4. PREPARE DATA FOR POSTGRESQL
# --------------------------------------------------

def prepare_dataframe(name, dataframe):

    df = dataframe.copy()

    # Convert financial values into Decimal.
    for column, precision in (
        DECIMAL_COLUMNS.get(name, {}).items()
    ):

        df[column] = df[column].map(

            lambda value: to_decimal(
                value,
                precision
            )
        )

    # Convert calendar dates into Python dates.
    for column in DATE_COLUMNS.get(name, []):

        df[column] = pd.to_datetime(
            df[column],
            errors="raise"
        ).dt.date

    # Convert categorical values into strings.
    for column in df.select_dtypes(
        include=["category"]
    ).columns:

        df[column] = df[column].astype(
            "string"
        )

    return df


# --------------------------------------------------
# 5. READ AND VERIFY SILVER DATASETS
# --------------------------------------------------

def read_silver_datasets(batch_dir):

    manifest_path = batch_dir / "manifest.json"

    with open(manifest_path, "r") as file:

        manifest = json.load(file)

    if manifest.get("status") != "success":

        raise ValueError(
            "Silver manifest does not indicate success."
        )

    entries = manifest["datasets"]

    names = [
        entry["dataset"]
        for entry in entries
    ]

    if (
        set(names) != set(DATASETS)
        or len(names) != len(DATASETS)
    ):

        raise ValueError(
            "Silver manifest is incomplete."
        )

    datasets = {}

    for entry in entries:

        name = entry["dataset"]

        file_path = batch_dir / entry["filename"]

        actual_checksum = hashlib.sha256(
            file_path.read_bytes()
        ).hexdigest()

        if actual_checksum != entry["sha256"]:

            raise ValueError(
                f"Checksum mismatch: {name}"
            )

        dataframe = pd.read_parquet(
            file_path
        )

        if len(dataframe) != entry["output_rows"]:

            raise ValueError(
                f"Record count mismatch: {name}"
            )

        datasets[name] = prepare_dataframe(
            name,
            dataframe
        )

    return datasets, manifest


# --------------------------------------------------
# 6. LOAD DATA IN A SINGLE TRANSACTION
# --------------------------------------------------

def load_snapshot(engine, datasets, manifest, batch_name):

    if set(datasets) != set(DATASETS):

        raise ValueError(
            "Required datasets are missing."
        )

    expected_counts = {

        name: len(datasets[name])

        for name in DATASETS
    }

    total_records = sum(
        expected_counts.values()
    )

    if total_records != manifest["total_output_rows"]:

        raise ValueError(
            "Total Silver record count mismatch."
        )

    with engine.begin() as connection:

        # Prevent simultaneous snapshot refreshes.
        connection.execute(
            text(
                "SELECT pg_advisory_xact_lock(42001)"
            )
        )

        # Full refresh of the six data tables.
        # All related tables are truncated together.
        # Load history is preserved.
        connection.execute(

            text(
                """
                TRUNCATE TABLE
                    silver.payments,
                    silver.transactions,
                    silver.loans,
                    silver.accounts,
                    silver.customers,
                    silver.branches
                """
            )
        )

        print(
            "\nExisting database snapshot cleared "
            "inside transaction.\n"
        )

        # Parent tables are loaded before child tables.
        for name in DATASETS:

            dataframe = datasets[name]

            dataframe.to_sql(
                name=name,
                con=connection,
                schema="silver",
                if_exists="append",
                index=False,
                chunksize=1000,
                dtype=SQL_DTYPES.get(name, {})
            )

            print(
                f"[LOADED] {name}: "
                f"{len(dataframe)} records"
            )

        # Validate record counts before committing.
        actual_counts = {}

        for name in DATASETS:

            count = connection.execute(

                text(
                    f"SELECT COUNT(*) "
                    f"FROM silver.{name}"
                )

            ).scalar_one()

            actual_counts[name] = count

            if count != expected_counts[name]:

                raise ValueError(
                    f"Database count mismatch: {name}"
                )

        # Record successful load metadata.
        connection.execute(

            text(
                """
                INSERT INTO silver.load_history (

                    source_silver_batch,

                    source_bronze_batch,

                    total_records,

                    table_counts,

                    status

                )

                VALUES (

                    :silver_batch,

                    :bronze_batch,

                    :total_records,

                    CAST(:table_counts AS JSONB),

                    'success'
                )
                """
            ),

            {

                "silver_batch": batch_name,

                "bronze_batch":
                    manifest["source_bronze_batch"],

                "total_records": total_records,

                "table_counts": json.dumps(
                    actual_counts
                        )
            }
        )

    # Reaching this point means the transaction committed.
    return actual_counts


# --------------------------------------------------
# 7. MAIN LOADING PIPELINE
# --------------------------------------------------

def load_silver():

    print("\nValidating Silver source data...")

    batch_dir = get_latest_silver_batch()

    validate_silver()

    if get_latest_silver_batch() != batch_dir:

        raise RuntimeError(
            "Latest Silver batch changed during validation. "
            "Retry the load."
        )

    datasets, manifest = read_silver_datasets(
        batch_dir
    )

    engine = get_engine()

    print("\nStarting PostgreSQL loading pipeline...")

    print(f"Source batch: {batch_dir.name}")

    try:

        counts = load_snapshot(

            engine,

            datasets,

            manifest,

            batch_dir.name
        )

        print(
            "\nDatabase transaction committed successfully!"
        )

        print(
            f"Total records loaded: {sum(counts.values())}"
        )

    except Exception:

        print(
            "\nDatabase loading failed. "
            "Uncommitted changes were rolled back."
        )

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":

    load_silver()
