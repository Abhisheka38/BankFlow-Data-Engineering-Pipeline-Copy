
import pandas as pd

from src.preprocessing.clean_data import (
    basic_cleaning,
    normalize_ids,
    normalize_categories,
    convert_dates,
    convert_numeric,
    split_invalid_records
)


# --------------------------------------------------
# 1. PRIMARY KEYS
# --------------------------------------------------

PRIMARY_KEYS = {
    "branches": "branch_id",
    "customers": "customer_id",
    "accounts": "account_id",
    "transactions": "transaction_id",
    "loans": "loan_id",
    "payments": "payment_id"
}


# --------------------------------------------------
# 2. REQUIRED COLUMNS
# --------------------------------------------------

REQUIRED_COLUMNS = {

    "branches": [
        "branch_id",
        "branch_name",
        "city",
        "district",
        "province",
        "opened_date"
    ],

    "customers": [
        "customer_id",
        "first_name",
        "last_name",
        "date_of_birth",
        "registration_date",
        "home_branch_id",
        "customer_status"
    ],

    "accounts": [
        "account_id",
        "customer_id",
        "branch_id",
        "account_type",
        "currency",
        "opened_date",
        "current_balance",
        "account_status"
    ],

    "transactions": [
        "transaction_id",
        "account_id",
        "branch_id",
        "transaction_timestamp",
        "transaction_type",
        "amount",
        "currency",
        "transaction_status"
    ],

    "loans": [
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

    "payments": [
        "payment_id",
        "loan_id",
        "payment_date",
        "amount_paid",
        "payment_status"
    ]
}


# --------------------------------------------------
# 3. BRANCH TRANSFORMATION
# --------------------------------------------------

def transform_branches(df):

    df = normalize_ids(
        df, ["branch_id"]
    )

    df = normalize_categories(
        df,
        ["branch_name", "city", "district", "province"]
    )

    df = convert_dates(
        df, ["opened_date"]
    )

    return df


# --------------------------------------------------
# 4. CUSTOMER TRANSFORMATION
# --------------------------------------------------

def transform_customers(df, as_of_date):

    df = normalize_ids(
        df,
        ["customer_id", "home_branch_id"]
    )

    df = normalize_categories(
        df,
        [
            "first_name",
            "last_name",
            "gender",
            "city",
            "occupation",
            "customer_status"
        ]
    )

    df = convert_dates(
        df,
        ["date_of_birth", "registration_date"]
    )

    df["full_name"] = (
        df["first_name"] + " " + df["last_name"]
    )

    reference_date = pd.Timestamp(as_of_date)

    dob = df["date_of_birth"]

    birthday_not_reached = (
        (dob.dt.month > reference_date.month)
        |
        (
            (dob.dt.month == reference_date.month)
            &
            (dob.dt.day > reference_date.day)
        )
    )

    df["customer_age"] = (
        reference_date.year
        - dob.dt.year
        - birthday_not_reached.astype(int)
    ).astype("Int64")

    df["age_group"] = pd.cut(
        df["customer_age"],
        bins=[0, 17, 25, 35, 45, 60, float("inf")],
        labels=[
            "Under 18",
            "18-25",
            "26-35",
            "36-45",
            "46-60",
            "61+"
        ],
        include_lowest=True
    )

    return df


# --------------------------------------------------
# 5. ACCOUNT TRANSFORMATION
# --------------------------------------------------

def transform_accounts(df):

    df = normalize_ids(
        df,
        ["account_id", "customer_id", "branch_id"]
    )

    df = normalize_categories(
        df,
        ["account_type", "account_status"]
    )

    df["currency"] = (
        df["currency"].str.upper()
    )

    df = convert_dates(
        df, ["opened_date"]
    )

    df = convert_numeric(
        df, ["current_balance"]
    )

    df["balance_category"] = pd.cut(
        df["current_balance"],
        bins=[
            0,
            10000,
            100000,
            1000000,
            float("inf")
        ],
        labels=[
            "Low",
            "Medium",
            "High",
            "Very High"
        ],
        include_lowest=True
    )

    return df


# --------------------------------------------------
# 6. TRANSACTION TRANSFORMATION
# --------------------------------------------------

def transform_transactions(df):

    df = normalize_ids(
        df,
        ["transaction_id", "account_id", "branch_id"]
    )

    df = normalize_categories(
        df,
        [
            "transaction_type",
            "transaction_status",
            "description"
        ]
    )

    channel_mapping = {
        "atm": "ATM",
        "mobile banking": "Mobile Banking",
        "online banking": "Online Banking",
        "branch": "Branch"
    }

    df["channel"] = (
        df["channel"]
        .str.lower()
        .map(channel_mapping)
    )

    df["currency"] = (
        df["currency"].str.upper()
    )

    df["transaction_timestamp"] = pd.to_datetime(
        df["transaction_timestamp"],
        errors="coerce"
    )

    df = convert_numeric(
        df, ["amount"]
    )

    df["transaction_date"] = (
        df["transaction_timestamp"]
        .dt.normalize()
    )

    df["transaction_year"] = (
        df["transaction_timestamp"]
        .dt.year
        .astype("Int64")
    )

    df["transaction_month"] = (
        df["transaction_timestamp"]
        .dt.month
        .astype("Int64")
    )

    direction = df["transaction_type"].map({
        "Credit": 1,
        "Debit": -1
    })

    df["signed_amount"] = (
        df["amount"] * direction
    )

    df["realized_amount"] = (
        df["signed_amount"].where(
            df["transaction_status"] == "Successful",
            0
        )
    )

    return df


# --------------------------------------------------
# 7. LOAN TRANSFORMATION
# --------------------------------------------------

def transform_loans(df):

    df = normalize_ids(
        df,
        ["loan_id", "customer_id", "branch_id"]
    )

    df = normalize_categories(
        df,
        ["loan_type", "loan_status"]
    )

    df = convert_dates(
        df, ["loan_date"]
    )

    df = convert_numeric(
        df,
        [
            "principal_amount",
            "annual_interest_rate",
            "term_months"
        ]
    )

    df["annual_interest_rate_decimal"] = (
        df["annual_interest_rate"] / 100
    )

    def calculate_maturity(row):

        loan_date = row["loan_date"]
        term = row["term_months"]

        if pd.isna(loan_date) or pd.isna(term):
            return pd.NaT

        if term not in [12, 24, 36, 48, 60]:
            return pd.NaT

        return loan_date + pd.DateOffset(
            months=int(term)
        )

    df["maturity_date"] = pd.to_datetime(
        df.apply(calculate_maturity, axis=1)
    )

    return df


# --------------------------------------------------
# 8. PAYMENT TRANSFORMATION
# --------------------------------------------------

def transform_payments(df):

    df = normalize_ids(
        df, ["payment_id", "loan_id"]
    )

    df = normalize_categories(
        df,
        ["payment_method", "payment_status"]
    )

    df = convert_dates(
        df, ["payment_date"]
    )

    df = convert_numeric(
        df, ["amount_paid"]
    )

    df["payment_year"] = (
        df["payment_date"].dt.year.astype("Int64")
    )

    df["payment_month"] = (
        df["payment_date"].dt.month.astype("Int64")
    )

    df["realized_payment_amount"] = (
        df["amount_paid"].where(
            df["payment_status"] == "Paid",
            0
        )
    )

    return df


# --------------------------------------------------
# 9. BUSINESS RULES
# --------------------------------------------------

def get_business_rules(name, df, as_of_date):

    if name == "branches":

        return [
            (
                df["opened_date"] > as_of_date,
                "Branch opening date is in the future"
            )
        ]

    if name == "customers":

        return [
            (
                ~df["customer_age"].between(0, 120),
                "Invalid customer age"
            ),
            (
                df["registration_date"] < df["date_of_birth"],
                "Registration before date of birth"
            ),
            (
                df["registration_date"] > as_of_date,
                "Future registration date"
            ),
            (
                ~df["customer_status"].isin(
                    ["Active", "Inactive"]
                ),
                "Invalid customer status"
            )
        ]

    if name == "accounts":

        return [
            (
                df["current_balance"] < 0,
                "Negative account balance"
            ),
            (
                ~df["account_type"].isin(
                    ["Savings", "Current", "Fixed Deposit"]
                ),
                "Invalid account type"
            ),
            (
                ~df["account_status"].isin(
                    ["Active", "Inactive", "Closed"]
                ),
                "Invalid account status"
            ),
            (
                df["currency"] != "LKR",
                "Unsupported currency"
            )
        ]

    if name == "transactions":

        return [
            (
                df["amount"] <= 0,
                "Invalid transaction amount"
            ),
            (
                ~df["transaction_type"].isin(
                    ["Credit", "Debit"]
                ),
                "Invalid transaction type"
            ),
            (
                ~df["transaction_status"].isin(
                    ["Successful", "Pending", "Failed"]
                ),
                "Invalid transaction status"
            ),
            (
                df["channel"].isna(),
                "Invalid transaction channel"
            ),
            (
                df["currency"] != "LKR",
                "Unsupported currency"
            )
        ]

    if name == "loans":

        return [
            (
                df["principal_amount"] <= 0,
                "Invalid loan principal"
            ),
            (
                ~df["annual_interest_rate"].between(0, 100),
                "Invalid annual interest rate"
            ),
            (
                ~df["term_months"].isin(
                    [12, 24, 36, 48, 60]
                ),
                "Invalid loan term"
            ),
            (
                ~df["loan_status"].isin(
                    ["Active", "Closed", "Defaulted"]
                ),
                "Invalid loan status"
            ),
            (
                ~df["loan_type"].isin(
                    ["Personal", "Housing", "Vehicle", "Business"]
                ),
                "Invalid loan type"
            )
        ]

    if name == "payments":

        return [
            (
                df["amount_paid"] <= 0,
                "Invalid payment amount"
            ),
            (
                ~df["payment_status"].isin(
                    ["Paid", "Pending", "Failed"]
                ),
                "Invalid payment status"
            )
        ]

    return []


# --------------------------------------------------
# 10. MAIN DATASET CLEANING FUNCTION
# --------------------------------------------------

def transform_dataset(name, dataframe, as_of_date):

    df, duplicate_count = basic_cleaning(
        dataframe
    )

    transformations = {
        "branches": transform_branches,
        "accounts": transform_accounts,
        "transactions": transform_transactions,
        "loans": transform_loans,
        "payments": transform_payments
    }

    if name == "customers":

        df = transform_customers(
            df, as_of_date
        )

    else:

        df = transformations[name](df)

    rejected_parts = []

    # Remove duplicates that become identical
    # after standardization.
    normalized_duplicates = int(
        df.duplicated().sum()
    )

    df = df.drop_duplicates().reset_index(drop=True)

    duplicate_count += normalized_duplicates

    # Reject records with missing required fields.
    missing_mask = df[
        REQUIRED_COLUMNS[name]
    ].isna().any(axis=1)

    df, rejected = split_invalid_records(
        df,
        missing_mask,
        "Missing or invalid required field"
    )

    rejected_parts.append(rejected)

    # Reject conflicting primary keys.
    primary_key = PRIMARY_KEYS[name]

    duplicate_mask = df[primary_key].duplicated(
        keep=False
    )

    df, rejected = split_invalid_records(
        df,
        duplicate_mask,
        "Conflicting duplicate primary key"
    )

    rejected_parts.append(rejected)

    # Apply business rules.
    for invalid_mask, reason in get_business_rules(
        name, df, as_of_date
    ):

        invalid_mask = invalid_mask.reindex(
            df.index
        )

        df, rejected = split_invalid_records(
            df,
            invalid_mask,
            reason
        )

        rejected_parts.append(rejected)

    rejected_df = pd.concat(
        rejected_parts,
        ignore_index=True
    )

    return (
        df.reset_index(drop=True),
        rejected_df,
        duplicate_count
    )
