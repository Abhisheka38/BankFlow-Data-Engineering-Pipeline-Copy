
import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

BRONZE_DIR = BASE_DIR / "data" / "raw" / "bronze"

PROFILE_DIR = (
    BASE_DIR / "data" / "processed" / "profiles"
)


def get_latest_batch():

    batches = sorted(
        path for path in BRONZE_DIR.glob("run_id=*")
        if path.is_dir()
    )

    if not batches:
        raise FileNotFoundError(
            "No Bronze batches found."
        )

    return batches[-1]


def profile_dataset(dataframe, filename):

    profile = {
        "dataset": filename,
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "duplicate_rows": int(
            dataframe.duplicated().sum()
        ),
        "missing_values": int(
            dataframe.isna().sum().sum()
        ),
        "columns": {}
    }

    for column in dataframe.columns:

        profile["columns"][column] = {
            "data_type": str(
                dataframe[column].dtype
            ),
            "missing_count": int(
                dataframe[column].isna().sum()
            ),
            "unique_count": int(
                dataframe[column].nunique()
            )
        }

    return profile


def run_profiling():

    batch_dir = get_latest_batch()

    output_dir = PROFILE_DIR / batch_dir.name

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    profiles = []

    print("\nStarting Bronze data profiling...")
    print(f"Batch: {batch_dir.name}\n")

    for file_path in sorted(
        batch_dir.glob("*.csv")
    ):

        dataframe = pd.read_csv(file_path)

        profile = profile_dataset(
            dataframe,
            file_path.name
        )

        profiles.append(profile)

        print(f"Dataset: {file_path.name}")
        print(f"Rows: {profile['row_count']}")
        print(f"Columns: {profile['column_count']}")
        print(f"Duplicates: {profile['duplicate_rows']}")
        print(f"Missing values: {profile['missing_values']}")
        print("-" * 40)

    report_path = output_dir / "profile_report.json"

    with open(report_path, "w") as file:

        json.dump(
            profiles,
            file,
            indent=4
        )

    print("\nData profiling completed.")
    print(f"Report: {report_path}")


if __name__ == "__main__":

    run_profiling()
