
import pandas as pd

from src.preprocessing.clean_data import (
    standardize_columns,
    clean_text_columns,
    normalize_ids,
    convert_numeric,
    convert_dates,
    remove_exact_duplicates,
    split_invalid_records
)

from src.transformation.silver_transform import (
    transform_dataset
)


def test_standardize_columns():

    df = pd.DataFrame({
        " Customer ID ": ["C001"],
        "First Name": ["Amal"]
    })

    result = standardize_columns(df)

    assert list(result.columns) == [
        "customer_id",
        "first_name"
    ]


def test_clean_text():

    df = pd.DataFrame({
        "city": [" Colombo ", " Kandy "]
    })

    result = clean_text_columns(df)

    assert result["city"].tolist() == [
        "Colombo",
        "Kandy"
    ]


def test_empty_string():

    df = pd.DataFrame({
        "city": ["   "]
    })

    result = clean_text_columns(df)

    assert pd.isna(
        result.loc[0, "city"]
    )


def test_normalize_ids():

    df = pd.DataFrame({
        "customer_id": ["cust001"]
    })

    result = normalize_ids(
        df, ["customer_id"]
    )

    assert result.loc[0, "customer_id"] == "CUST001"


def test_numeric_conversion():

    df = pd.DataFrame({
        "amount": ["1000", "invalid"]
    })

    result = convert_numeric(
        df, ["amount"]
    )

    assert result.loc[0, "amount"] == 1000

    assert pd.isna(
        result.loc[1, "amount"]
    )


def test_invalid_date():

    df = pd.DataFrame({
        "date": ["2025-01-01", "invalid"]
    })

    result = convert_dates(
        df, ["date"]
    )

    assert result.loc[0, "date"] == pd.Timestamp(
        "2025-01-01"
    )

    assert pd.isna(
        result.loc[1, "date"]
    )


def test_duplicate_removal():

    df = pd.DataFrame({
        "customer_id": ["C001", "C001", "C002"]
    })

    result, removed = remove_exact_duplicates(
        df
    )

    assert len(result) == 2

    assert removed == 1


def test_quarantine():

    df = pd.DataFrame({
        "amount": [1000, -500, 2000]
    })

    valid, rejected = split_invalid_records(
        df,
        df["amount"] < 0,
        "Negative amount"
    )

    assert len(valid) == 2

    assert len(rejected) == 1

    assert rejected.iloc[0][
        "rejection_reason"
    ] == "Negative amount"


def test_transaction_transformation():

    df = pd.DataFrame({

        "transaction_id": [
            "TXN001",
            "TXN002",
            "TXN003",
            "TXN004"
        ],

        "account_id": [
            "ACC001",
            "ACC001",
            "ACC001",
            "ACC001"
        ],

        "branch_id": [
            "BR001",
            "BR001",
            "BR001",
            "BR001"
        ],

        "transaction_timestamp": [
            "2025-01-01 10:00:00"
        ] * 4,

        "transaction_type": [
            "Credit",
            "Debit",
            "Credit",
            "Debit"
        ],

        "amount": [
            1000,
            500,
            2000,
            -100
        ],

        "currency": ["LKR"] * 4,

        "channel": ["ATM"] * 4,

        "transaction_status": [
            "Successful",
            "Successful",
            "Pending",
            "Successful"
        ],

        "description": [
            "Fund Transfer"
        ] * 4
    })

    valid, rejected, duplicates = transform_dataset(
        "transactions",
        df,
        pd.Timestamp("2026-11-25")
    )

    assert len(valid) == 3

    assert len(rejected) == 1

    assert duplicates == 0

    assert valid["signed_amount"].tolist() == [
        1000,
        -500,
        2000
    ]

    assert valid["realized_amount"].tolist() == [
        1000,
        -500,
        0
    ]
