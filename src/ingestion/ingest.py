
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_DIR = BASE_DIR / "data" / "sample"

BRONZE_DIR = BASE_DIR / "data" / "raw" / "bronze"

BRONZE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. EXPECTED DATASET SCHEMAS
# --------------------------------------------------

EXPECTED_COLUMNS = {

    "branches.csv": [
        "branch_id",
        "branch_name",
        "city",
        "district",
        "province",
        "opened_date"
    ],

    "customers.csv": [
        "customer_id",
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
        "city",
        "occupation",
        "registration_date",
        "home_branch_id",
        "customer_status"
    ],

    "accounts.csv": [
        "account_id",
        "customer_id",
        "branch_id",
        "account_type",
        "currency",
        "opened_date",
        "current_balance",
        "account_status"
    ],

    "transactions.csv": [
        "transaction_id",
        "account_id",
        "branch_id",
        "transaction_timestamp",
        "transaction_type",
        "amount",
        "currency",
        "channel",
        "transaction_status",
        "description"
    ],

    "loans.csv": [
        "loan_id",
        "customer_id",
        "branch_id",
        "loan_type",
        "principal_amount",
        "annual_interest_rate",
        "term_months",
        "loan_date",
        "loan_status"
    ],

    "payments.csv": [
        "payment_id",
        "loan_id",
        "payment_date",
        "amount_paid",
        "payment_method",
        "payment_status"
    ]
}


# --------------------------------------------------
# 3. GENERATE FILE CHECKSUM
# --------------------------------------------------

def calculate_checksum(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(8192), b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


# --------------------------------------------------
# 4. VALIDATE SOURCE FILE
# --------------------------------------------------

def validate_source_file(file_path, expected_columns):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    dataframe = pd.read_csv(file_path)

    if dataframe.empty:
        raise ValueError(
            f"Dataset is empty: {file_path.name}"
        )

    actual_columns = list(dataframe.columns)

    if actual_columns != expected_columns:
        raise ValueError(
            f"Schema mismatch in {file_path.name}\n"
            f"Expected: {expected_columns}\n"
            f"Actual: {actual_columns}"
        )

    return dataframe


# --------------------------------------------------
# 5. MAIN INGESTION PIPELINE
# --------------------------------------------------

def ingest_data():

    current_time = datetime.now(timezone.utc)

    run_id = current_time.strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    batch_dir = BRONZE_DIR / f"run_id={run_id}"

    staging_dir = BRONZE_DIR / f".staging_{run_id}"

    staging_dir.mkdir(parents=True, exist_ok=False)

    manifest = {
        "project": "BankFlow",
        "layer": "bronze",
        "run_id": run_id,
        "ingestion_timestamp": current_time.isoformat(),
        "datasets": []
    }

    total_records = 0

    print("\nStarting BankFlow ingestion pipeline...")
    print(f"Run ID: {run_id}\n")

    try:

        for filename, expected_columns in EXPECTED_COLUMNS.items():

            source_file = SOURCE_DIR / filename

            destination_file = staging_dir / filename

            # Validate source data
            dataframe = validate_source_file(
                source_file,
                expected_columns
            )

            # Calculate original file checksum
            source_checksum = calculate_checksum(
                source_file
            )

            # Copy original file to Bronze staging
            shutil.copy2(
                source_file,
                destination_file
            )

            # Verify copied file integrity
            destination_checksum = calculate_checksum(
                destination_file
            )

            if source_checksum != destination_checksum:

                raise ValueError(
                    f"Checksum mismatch: {filename}"
                )

            row_count = len(dataframe)

            total_records += row_count

            # Store dataset metadata
            dataset_metadata = {
                "filename": filename,
                "row_count": row_count,
                "columns": list(dataframe.columns),
                "file_size_bytes": destination_file.stat().st_size,
                "sha256": destination_checksum
            }

            manifest["datasets"].append(
                dataset_metadata
            )

            print(
                f"[SUCCESS] {filename}: "
                f"{row_count} records ingested"
            )

        manifest["total_records"] = total_records

        manifest["status"] = "success"

        # Save ingestion metadata
        manifest_path = staging_dir / "manifest.json"

        with open(manifest_path, "w") as file:

            json.dump(
                manifest,
                file,
                indent=4
            )

        # Publish only a successfully completed batch
        staging_dir.rename(batch_dir)

    except Exception:

        # Remove incomplete batch
        shutil.rmtree(
            staging_dir,
            ignore_errors=True
        )

        raise

    print("\nIngestion completed successfully!")

    print(f"Total records: {total_records}")

    print(f"Bronze location: {batch_dir}")


# --------------------------------------------------
# 6. RUN PIPELINE
# --------------------------------------------------

if __name__ == "__main__":

    ingest_data()
