
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.validation.validate_bronze import (
    validate_bronze
)

from src.preprocessing.clean_data import (
    split_invalid_records
)

from src.transformation.silver_transform import (
    transform_dataset
)


BASE_DIR = Path(__file__).resolve().parents[2]

BRONZE_DIR = BASE_DIR / "data" / "raw" / "bronze"

SILVER_DIR = (
    BASE_DIR / "data" / "processed" / "silver"
)

QUARANTINE_DIR = (
    BASE_DIR / "data" / "processed" / "quarantine"
)

DATASETS = [
    "branches",
    "customers",
    "accounts",
    "transactions",
    "loans",
    "payments"
]


# --------------------------------------------------
# 1. LOCATE BRONZE BATCH
# --------------------------------------------------

def get_latest_bronze_batch():

    batches = sorted(
        path for path in BRONZE_DIR.glob("run_id=*")
        if path.is_dir()
    )

    if not batches:

        raise FileNotFoundError(
            "No Bronze batches found."
        )

    return batches[-1]


# --------------------------------------------------
# 2. CHECKSUM
# --------------------------------------------------

def calculate_checksum(path):

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


# --------------------------------------------------
# 3. FOREIGN KEY VALIDATION
# --------------------------------------------------

def enforce_relationships(cleaned, rejected):

    relationships = [

        ("customers", "home_branch_id",
         "branches", "branch_id"),

        ("accounts", "customer_id",
         "customers", "customer_id"),

        ("accounts", "branch_id",
         "branches", "branch_id"),

        ("transactions", "account_id",
         "accounts", "account_id"),

        ("transactions", "branch_id",
         "branches", "branch_id"),

        ("loans", "customer_id",
         "customers", "customer_id"),

        ("loans", "branch_id",
         "branches", "branch_id"),

        ("payments", "loan_id",
         "loans", "loan_id")
    ]

    for child, child_key, parent, parent_key in relationships:

        invalid_mask = (
            ~cleaned[child][child_key].isin(
                cleaned[parent][parent_key]
            )
        )

        valid, invalid = split_invalid_records(
            cleaned[child],
            invalid_mask,
            f"Invalid foreign key: {child_key} -> {parent}"
        )

        cleaned[child] = valid

        rejected[child] = pd.concat(
            [rejected[child], invalid],
            ignore_index=True
        )


# --------------------------------------------------
# 4. MAIN SILVER PIPELINE
# --------------------------------------------------

def run_silver():

    # Strict Day 2 validation gate.
    validate_bronze()

    bronze_batch = get_latest_bronze_batch()

    with open(bronze_batch / "manifest.json") as file:

        bronze_manifest = json.load(file)

    # Use the Bronze ingestion date for reproducible
    # age calculations when reprocessing a batch.
    as_of_date = (
        pd.Timestamp(
            bronze_manifest["ingestion_timestamp"]
        )
        .tz_localize(None)
        .normalize()
    )

    current_time = datetime.now(timezone.utc)

    run_id = current_time.strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    QUARANTINE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    silver_batch = SILVER_DIR / f"run_id={run_id}"

    quarantine_batch = (
        QUARANTINE_DIR / f"run_id={run_id}"
    )

    silver_staging = (
        SILVER_DIR / f".staging_{run_id}"
    )

    quarantine_staging = (
        QUARANTINE_DIR / f".staging_{run_id}"
    )

    cleaned = {}
    rejected = {}
    input_counts = {}
    duplicate_counts = {}

    print("\nStarting BankFlow Silver pipeline...")
    print(f"Bronze batch: {bronze_batch.name}")
    print(f"Silver run ID: {run_id}\n")

    try:

        silver_staging.mkdir()
        quarantine_staging.mkdir()

        # Transform all datasets.
        for name in DATASETS:

            source_path = (
                bronze_batch / f"{name}.csv"
            )

            dataframe = pd.read_csv(
                source_path
            )

            input_counts[name] = len(dataframe)

            valid, invalid, duplicates = (
                transform_dataset(
                    name,
                    dataframe,
                    as_of_date
                )
            )

            cleaned[name] = valid
            rejected[name] = invalid
            duplicate_counts[name] = duplicates

        # Validate foreign keys after cleaning.
        enforce_relationships(
            cleaned,
            rejected
        )

        manifest = {
            "project": "BankFlow",
            "layer": "silver",
            "run_id": run_id,
            "source_bronze_batch": bronze_batch.name,
            "processing_timestamp": current_time.isoformat(),
            "as_of_date": str(as_of_date.date()),
            "datasets": []
        }

        # Save transformed datasets.
        for name in DATASETS:

            valid = cleaned[name]
            invalid = rejected[name]

            output_path = (
                silver_staging / f"{name}.parquet"
            )

            valid.to_parquet(
                output_path,
                engine="pyarrow",
                compression="snappy",
                index=False
            )

            quarantine_filename = None

            if not invalid.empty:

                quarantine_filename = f"{name}_rejected.csv"

                invalid.to_csv(
                    quarantine_staging / quarantine_filename,
                    index=False
                )

            input_rows = input_counts[name]
            output_rows = len(valid)
            rejected_rows = len(invalid)
            duplicates = duplicate_counts[name]

            # Ensure every input record is accounted for.
            if input_rows != (
                output_rows + rejected_rows + duplicates
            ):

                raise ValueError(
                    f"Record reconciliation failed: {name}"
                )

            manifest["datasets"].append({

                "dataset": name,

                "filename": output_path.name,

                "input_rows": input_rows,

                "output_rows": output_rows,

                "rejected_rows": rejected_rows,

                "duplicates_removed": duplicates,

                "quarantine_file": quarantine_filename,

                "columns": list(valid.columns),

                "data_types": {
                    column: str(dtype)
                    for column, dtype in valid.dtypes.items()
                },

                "file_size_bytes": (
                    output_path.stat().st_size
                ),

                "sha256": calculate_checksum(
                    output_path
                )
            })

            print(
                f"[SUCCESS] {name}: "
                f"input={input_rows}, "
                f"clean={output_rows}, "
                f"rejected={rejected_rows}, "
                f"duplicates={duplicates}"
            )

        manifest["total_input_rows"] = sum(
            input_counts.values()
        )

        manifest["total_output_rows"] = sum(
            len(df) for df in cleaned.values()
        )

        manifest["total_rejected_rows"] = sum(
            len(df) for df in rejected.values()
        )

        manifest["total_duplicates_removed"] = sum(
            duplicate_counts.values()
        )

        manifest["status"] = "success"

        with open(
            silver_staging / "manifest.json",
            "w"
        ) as file:

            json.dump(
                manifest,
                file,
                indent=4
            )

        # Publish quarantine first, then Silver.
        quarantine_staging.rename(
            quarantine_batch
        )

        silver_staging.rename(
            silver_batch
        )

    except Exception:

        shutil.rmtree(
            silver_staging,
            ignore_errors=True
        )

        shutil.rmtree(
            quarantine_staging,
            ignore_errors=True
        )

        if not silver_batch.exists():

            shutil.rmtree(
                quarantine_batch,
                ignore_errors=True
            )

        raise

    print("\nSilver pipeline completed successfully!")

    print(
        f"Input rows: "
        f"{manifest['total_input_rows']}"
    )

    print(
        f"Clean rows: "
        f"{manifest['total_output_rows']}"
    )

    print(
        f"Rejected rows: "
        f"{manifest['total_rejected_rows']}"
    )

    print(
        f"Duplicates removed: "
        f"{manifest['total_duplicates_removed']}"
    )

    print(f"Silver location: {silver_batch}")

    print(f"Quarantine location: {quarantine_batch}")


if __name__ == "__main__":

    run_silver()
