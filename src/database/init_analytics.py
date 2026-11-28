
from pathlib import Path

from src.database.connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[2]

ANALYTICS_DIR = BASE_DIR / "sql" / "analytics"

SQL_FILES = [
    "01_create_analytics_schema.sql",
    "05_analytical_views.sql",
    "06_materialized_views.sql",
    "07_stored_procedures.sql"
]


def initialize_analytics():

    engine = get_engine()

    print("\nInitializing BankFlow analytics...\n")

    try:

        with engine.begin() as connection:

            for filename in SQL_FILES:

                file_path = ANALYTICS_DIR / filename

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

                # Execute the complete SQL script.
                # Do not split stored procedures
                # using semicolons.
                connection.exec_driver_sql(
                    sql_script
                )

                print(
                    f"[EXECUTED] {filename}"
                )

        print(
            "\nAnalytics initialization completed!"
        )

    except Exception:

        print(
            "\nAnalytics initialization failed. "
            "Uncommitted changes were rolled back."
        )

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":

    initialize_analytics()
