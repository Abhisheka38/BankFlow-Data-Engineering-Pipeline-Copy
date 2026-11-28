
from pathlib import Path

from src.database.connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[2]

WAREHOUSE_SQL_DIR = BASE_DIR / "sql" / "warehouse"

SQL_FILES = [
    "01_create_warehouse_schema.sql",
    "02_create_dimensions.sql",
    "03_create_facts.sql",
    "04_create_warehouse_indexes.sql"
]


def initialize_warehouse():

    engine = get_engine()

    print("\nInitializing BankFlow data warehouse...\n")

    try:

        with engine.begin() as connection:

            for filename in SQL_FILES:

                file_path = WAREHOUSE_SQL_DIR / filename

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

                connection.exec_driver_sql(sql_script)

                print(f"[EXECUTED] {filename}")

        print(
            "\nData warehouse initialization completed!"
        )

    except Exception:

        print(
            "\nWarehouse initialization failed. "
            "Uncommitted changes were rolled back."
        )

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":

    initialize_warehouse()
