
import hashlib
import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

BRONZE_DIR = BASE_DIR / "data" / "raw" / "bronze"

EXPECTED_DATASETS = {
    "branches.csv",
    "customers.csv",
    "accounts.csv",
    "transactions.csv",
    "loans.csv",
    "payments.csv"
}


# --------------------------------------------------
# 2. FIND LATEST INGESTION BATCH
# --------------------------------------------------

def get_latest_batch():

    batches = sorted(
        path
        for path in BRONZE_DIR.glob("run_id=*")
        if path.is_dir()
    )

    if not batches:

        raise FileNotFoundError(
            "No Bronze ingestion batches found."
        )

    return batches[-1]


# --------------------------------------------------
# 3. CALCULATE FILE CHECKSUM
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
# 4. VALIDATE PRIMARY KEYS
# --------------------------------------------------

def validate_primary_key(
    dataframe,
    column,
    dataset_name
):

    null_count = dataframe[column].isna().sum()

    duplicate_count = dataframe[column].duplicated().sum()

    if null_count > 0 or duplicate_count > 0:

        print(
            f"[FAIL] {dataset_name}.{column}: "
            f"Nulls={null_count}, "
            f"Duplicates={duplicate_count}"
        )

        return False

    print(
        f"[PASS] Primary key: "
        f"{dataset_name}.{column}"
    )

    return True


# --------------------------------------------------
# 5. VALIDATE FOREIGN KEYS
# --------------------------------------------------

def validate_foreign_key(
    child_dataframe,
    child_column,
    parent_dataframe,
    parent_column,
    relationship_name
):

    invalid_mask = (
        child_dataframe[child_column].isna()
        |
        ~child_dataframe[child_column].isin(
            parent_dataframe[parent_column]
        )
    )

    invalid_count = invalid_mask.sum()

    if invalid_count > 0:

        print(
            f"[FAIL] {relationship_name}: "
            f"{invalid_count} invalid references"
        )

        return False

    print(
        f"[PASS] Foreign key: {relationship_name}"
    )

    return True


# --------------------------------------------------
# 6. VALIDATE BUSINESS RULES
# --------------------------------------------------

def validate_amount(
    dataframe,
    column,
    dataset_name,
    allow_zero=False
):

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce"
    )

    if allow_zero:

        invalid_mask = (
            values.isna() | (values < 0)
        )

    else:

        invalid_mask = (
            values.isna() | (values <= 0)
        )

    invalid_count = invalid_mask.sum()

    if invalid_count > 0:

        print(
            f"[FAIL] {dataset_name}.{column}: "
            f"{invalid_count} invalid values"
        )

        return False

    print(
        f"[PASS] Business rule: "
        f"{dataset_name}.{column}"
    )

    return True


# --------------------------------------------------
# 7. VALIDATE MANIFEST AND FILE INTEGRITY
# --------------------------------------------------

def validate_manifest(batch_dir):

    manifest_path = batch_dir / "manifest.json"

    if not manifest_path.exists():

        print("[FAIL] Manifest file not found")

        return False

    with open(manifest_path, "r") as file:

        manifest = json.load(file)

    results = []

    manifest_files = [
        dataset["filename"]
        for dataset in manifest["datasets"]
    ]

    complete = (
        set(manifest_files) == EXPECTED_DATASETS
        and len(manifest_files) == len(EXPECTED_DATASETS)
        and manifest.get("status") == "success"
    )

    results.append(complete)

    if not complete:

        print("[FAIL] Manifest dataset completeness")

        return False

    print("[PASS] Manifest dataset completeness")

    total_records = 0

    for dataset in manifest["datasets"]:

        filename = dataset["filename"]

        file_path = batch_dir / filename

        if not file_path.exists():

            print(f"[FAIL] Missing file: {filename}")

            results.append(False)

            continue

        actual_checksum = calculate_checksum(
            file_path
        )

        expected_checksum = dataset["sha256"]

        checksum_valid = (
            actual_checksum == expected_checksum
        )

        if checksum_valid:

            print(f"[PASS] Checksum: {filename}")

        else:

            print(f"[FAIL] Checksum: {filename}")

        results.append(checksum_valid)

        dataframe = pd.read_csv(file_path)

        actual_count = len(dataframe)

        total_records += actual_count

        row_count_valid = (
            actual_count == dataset["row_count"]
        )

        if row_count_valid:

            print(f"[PASS] Record count: {filename}")

        else:

            print(f"[FAIL] Record count: {filename}")

        results.append(row_count_valid)

    total_valid = (
        total_records == manifest["total_records"]
    )

    results.append(total_valid)

    print(
        f"[{'PASS' if total_valid else 'FAIL'}] "
        "Total record count"
    )

    return all(results)


# --------------------------------------------------
# 8. MAIN VALIDATION PIPELINE
# --------------------------------------------------

def validate_bronze():

    batch_dir = get_latest_batch()

    print("\nStarting Bronze data validation...")

    print(f"Batch: {batch_dir.name}\n")

    results = []

    # Validate manifest and file integrity first
    print("--- File Integrity Validation ---")

    integrity_valid = validate_manifest(batch_dir)

    if not integrity_valid:

        print("\nBronze file integrity validation failed.")

        raise SystemExit(1)

    results.append(integrity_valid)

    # Load datasets
    branches = pd.read_csv(
        batch_dir / "branches.csv"
    )

    customers = pd.read_csv(
        batch_dir / "customers.csv"
    )

    accounts = pd.read_csv(
        batch_dir / "accounts.csv"
    )

    transactions = pd.read_csv(
        batch_dir / "transactions.csv"
    )

    loans = pd.read_csv(
        batch_dir / "loans.csv"
    )

    payments = pd.read_csv(
        batch_dir / "payments.csv"
    )

    # Primary key validation
    print("\n--- Primary Key Validation ---")

    primary_keys = [
        (branches, "branch_id", "branches"),
        (customers, "customer_id", "customers"),
        (accounts, "account_id", "accounts"),
        (transactions, "transaction_id", "transactions"),
        (loans, "loan_id", "loans"),
        (payments, "payment_id", "payments")
    ]

    for dataframe, column, name in primary_keys:

        results.append(
            validate_primary_key(
                dataframe,
                column,
                name
            )
        )

    # Foreign key validation
    print("\n--- Foreign Key Validation ---")

    relationships = [

        (
            customers, "home_branch_id",
            branches, "branch_id",
            "customers -> branches"
        ),

        (
            accounts, "customer_id",
            customers, "customer_id",
            "accounts -> customers"
        ),

        (
            accounts, "branch_id",
            branches, "branch_id",
            "accounts -> branches"
        ),

        (
            transactions, "account_id",
            accounts, "account_id",
            "transactions -> accounts"
        ),

        (
            transactions, "branch_id",
            branches, "branch_id",
            "transactions -> branches"
        ),

        (
            loans, "customer_id",
            customers, "customer_id",
            "loans -> customers"
        ),

        (
            loans, "branch_id",
            branches, "branch_id",
            "loans -> branches"
        ),

        (
            payments, "loan_id",
            loans, "loan_id",
            "payments -> loans"
        )
    ]

    for relationship in relationships:

        results.append(
            validate_foreign_key(*relationship)
        )

    # Business rule validation
    print("\n--- Business Rule Validation ---")

    results.append(
        validate_amount(
            transactions,
            "amount",
            "transactions"
        )
    )

    results.append(
        validate_amount(
            accounts,
            "current_balance",
            "accounts",
            allow_zero=True
        )
    )

    results.append(
        validate_amount(
            loans,
            "principal_amount",
            "loans"
        )
    )

    results.append(
        validate_amount(
            payments,
            "amount_paid",
            "payments"
        )
    )

    # Final validation summary
    passed = sum(results)

    failed = len(results) - passed

    print("\n--- Validation Summary ---")

    print(f"Validation groups: {len(results)}")

    print(f"Passed: {passed}")

    print(f"Failed: {failed}")

    if all(results):

        print("\nBronze data validation successful!")

        print("Data is ready for Silver processing.")

    else:

        print("\nBronze data validation failed!")

        raise SystemExit(1)


# --------------------------------------------------
# 9. RUN VALIDATION
# --------------------------------------------------

if __name__ == "__main__":

    validate_bronze()
