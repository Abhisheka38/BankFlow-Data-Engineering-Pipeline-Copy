
import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. STANDARDIZE COLUMN NAMES
# --------------------------------------------------

def standardize_columns(dataframe):

    dataframe = dataframe.copy()

    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    if dataframe.columns.duplicated().any():

        raise ValueError(
            "Duplicate column names after standardization."
        )

    return dataframe


# --------------------------------------------------
# 2. CLEAN TEXT COLUMNS
# --------------------------------------------------

def clean_text_columns(dataframe):

    dataframe = dataframe.copy()

    text_columns = dataframe.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        dataframe[column] = (
            dataframe[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    return dataframe


# --------------------------------------------------
# 3. NORMALIZE IDENTIFIERS
# --------------------------------------------------

def normalize_ids(dataframe, columns):

    dataframe = dataframe.copy()

    for column in columns:

        dataframe[column] = (
            dataframe[column]
            .astype("string")
            .str.strip()
            .str.upper()
        )

    return dataframe


# --------------------------------------------------
# 4. STANDARDIZE CATEGORY VALUES
# --------------------------------------------------

def normalize_categories(dataframe, columns):

    dataframe = dataframe.copy()

    for column in columns:

        dataframe[column] = (
            dataframe[column]
            .astype("string")
            .str.strip()
            .str.title()
        )

    return dataframe


# --------------------------------------------------
# 5. CONVERT DATE COLUMNS
# --------------------------------------------------

def convert_dates(dataframe, columns):

    dataframe = dataframe.copy()

    for column in columns:

        dataframe[column] = pd.to_datetime(
            dataframe[column],
            errors="coerce",
            format="%Y-%m-%d"
        )

    return dataframe


# --------------------------------------------------
# 6. CONVERT NUMERIC COLUMNS
# --------------------------------------------------

def convert_numeric(dataframe, columns):

    dataframe = dataframe.copy()

    for column in columns:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

        dataframe[column] = (
            dataframe[column]
            .replace([np.inf, -np.inf], np.nan)
        )

    return dataframe


# --------------------------------------------------
# 7. REMOVE EXACT DUPLICATE ROWS
# --------------------------------------------------

def remove_exact_duplicates(dataframe):

    duplicate_count = int(
        dataframe.duplicated().sum()
    )

    cleaned = (
        dataframe
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return cleaned, duplicate_count


# --------------------------------------------------
# 8. QUARANTINE INVALID RECORDS
# --------------------------------------------------

def split_invalid_records(
    dataframe,
    invalid_mask,
    reason
):

    invalid_mask = invalid_mask.fillna(True)

    rejected = dataframe.loc[
        invalid_mask
    ].copy()

    valid = dataframe.loc[
        ~invalid_mask
    ].copy()

    rejected["rejection_reason"] = reason

    return valid, rejected


# --------------------------------------------------
# 9. COMMON CLEANING PIPELINE
# --------------------------------------------------

def basic_cleaning(dataframe):

    dataframe = standardize_columns(dataframe)

    dataframe = clean_text_columns(dataframe)

    dataframe, duplicate_count = (
        remove_exact_duplicates(dataframe)
    )

    return dataframe, duplicate_count
