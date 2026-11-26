
import hashlib
import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SILVER_DIR = (
    BASE_DIR / "data" / "processed" / "silver"
)

QUARANTINE_DIR = (
    BASE_DIR / "data" / "processed" / "quarantine"
)

PRIMARY_KEYS = {
    "branches": "branch_id",
    "customers": "customer_id",
    "accounts": "account_id",
    "transactions": "transaction_id",
    "loans": "loan_id",
    "payments": "payment_id"
}

DERIVED_COLUMNS = {
    "customers": [
        "full_name",
        "customer_age",
        "age_group"
    ],
    "accounts": [
        "balance_category"
    ],
    "transactions": [
        "transaction_date",
        "transaction_year",
        "transaction_month",
        "signed_amount",
        "realized_amount"
    ],
    "loans": [
        "annual_interest_rate_decimal",
        "maturity_date"
    ],
    "payments": [
        "payment_year",
        "payment_month",
        "realized_payment_amount"
    ]
}


def get_latest_batch():

    batches = sorted(
        path for path in SILVER_DIR.glob("run_id=*")
        if path.is_dir()
    )

    if not batches:

        raise FileNotFoundError(
            "No Silver batches found."
        )

    return batches[-1]


def check(condition, message, results):

    passed = bool(condition)

    results.append(passed)

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {message}")


def validate_silver():

    batch = get_latest_batch()

    with open(batch / "manifest.json") as file:

        manifest = json.load(file)

    results = []

    datasets = {}

    print("\nStarting Silver validation...")
    print(f"Batch: {batch.name}\n")

    entries = manifest["datasets"]

    names = [
        entry["dataset"] for entry in entries
    ]

    complete = (
        set(names) == set(PRIMARY_KEYS)
        and len(names) == len(PRIMARY_KEYS)
        and manifest.get("status") == "success"
    )

    check(
        complete,
        "Manifest completeness",
        results
    )

    if not complete:

        raise SystemExit(1)

    for entry in entries:

        name = entry["dataset"]

        path = batch / entry["filename"]

        if not path.exists():

            check(
                False,
                f"{name}: missing Parquet file",
                results
            )

            raise SystemExit(1)

        df = pd.read_parquet(path)

        datasets[name] = df

        checksum = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        check(
            checksum == entry["sha256"],
            f"{name}: checksum",
            results
        )

        check(
            len(df) == entry["output_rows"],
            f"{name}: output record count",
            results
        )

        check(
            entry["input_rows"] == (
                len(df)
                + entry["rejected_rows"]
                + entry["duplicates_removed"]
            ),
            f"{name}: record reconciliation",
            results
        )

        quarantine_file = entry["quarantine_file"]

        if entry["rejected_rows"] > 0:

            if quarantine_file:

                quarantine_path = (
                    QUARANTINE_DIR
                    / batch.name
                    / quarantine_file
                )

                quarantine_valid = (
                    quarantine_path.exists()
                    and len(
                        pd.read_csv(quarantine_path)
                    ) == entry["rejected_rows"]
                )

            else:

                quarantine_valid = False

            check(
                quarantine_valid,
                f"{name}: quarantine record count",
                results
            )

        primary_key = PRIMARY_KEYS[name]

        check(
            df[primary_key].notna().all()
            and df[primary_key].is_unique,
            f"{name}: primary key",
            results
        )

        required_derived = DERIVED_COLUMNS.get(
            name, []
        )

        check(
            set(required_derived).issubset(
                df.columns
            ),
            f"{name}: derived columns",
            results
        )

    # Foreign key validation
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

        check(
            datasets[child][child_key].notna().all()
            and datasets[child][child_key].isin(
                datasets[parent][parent_key]
            ).all(),
            f"{child}.{child_key} -> {parent}",
            results
        )

    # Date data types
    date_columns = {

        "branches": ["opened_date"],

        "customers": [
            "date_of_birth",
            "registration_date"
        ],

        "accounts": ["opened_date"],

        "transactions": [
            "transaction_timestamp",
            "transaction_date"
        ],

        "loans": [
            "loan_date",
            "maturity_date"
        ],

        "payments": ["payment_date"]
    }

    for name, columns in date_columns.items():

        for column in columns:

            check(
                pd.api.types.is_datetime64_any_dtype(
                    datasets[name][column]
                )
                and datasets[name][column].notna().all(),
                f"{name}.{column}: datetime type",
                results
            )

    # Financial data types and amount rules
    amount_columns = [
        ("accounts", "current_balance", True),
        ("transactions", "amount", False),
        ("loans", "principal_amount", False),
        ("payments", "amount_paid", False)
    ]

    for name, column, allow_zero in amount_columns:

        values = datasets[name][column]

        valid_type = pd.api.types.is_numeric_dtype(
            values
        )

        if valid_type:

            valid_amount = (
                values.ge(0).all()
                if allow_zero
                else values.gt(0).all()
            )

        else:

            valid_amount = False

        check(
            valid_type
            and values.notna().all()
            and valid_amount,
            f"{name}.{column}: financial validation",
            results
        )

    # Signed transaction amount validation
    transactions = datasets["transactions"]

    expected_signed = (
        transactions["amount"]
        * transactions["transaction_type"].map({
            "Credit": 1,
            "Debit": -1
        })
    )

    check(
        transactions["signed_amount"]
        .eq(expected_signed).all(),
        "Transaction signed amount",
        results
    )

    expected_realized = expected_signed.where(
        transactions["transaction_status"] == "Successful",
        0
    )

    check(
        transactions["realized_amount"]
        .eq(expected_realized).all(),
        "Transaction realized amount",
        results
    )

    # Realized loan payment validation
    payments = datasets["payments"]

    expected_payments = payments["amount_paid"].where(
        payments["payment_status"] == "Paid",
        0
    )

    check(
        payments["realized_payment_amount"]
        .eq(expected_payments).all(),
        "Realized loan payment amount",
        results
    )

    # Batch-level reconciliation
    total_output = sum(
        len(df) for df in datasets.values()
    )

    check(
        total_output == manifest["total_output_rows"],
        "Total Silver output records",
        results
    )

    check(
        manifest["total_input_rows"] == (
            total_output
            + manifest["total_rejected_rows"]
            + manifest["total_duplicates_removed"]
        ),
        "Total batch reconciliation",
        results
    )

    print("\n--- Validation Summary ---")

    print(f"Total checks: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if not all(results):

        print("\nSilver validation failed.")

        raise SystemExit(1)

    print("\nSilver validation successful!")
    print("Data is ready for downstream processing.")


if __name__ == "__main__":

    validate_silver()
