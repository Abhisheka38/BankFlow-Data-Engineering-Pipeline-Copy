from pathlib import Path

from src.database.connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[2]

SCHEMA_DIR = BASE_DIR / "sql" / "schema"

SQL_FILES = [
    "01_create_schema.sql",
    "02_create_tables.sql",
    "03_create_indexes.sql"
]


def initialize_database():

    engine = get_engine()

    print("\nInitializing BankFlow database...\n")

    try:

        with engine.begin() as connection:

            for filename in SQL_FILES:

                file_path = SCHEMA_DIR / filename

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

                statements = sql_script.split(";")

                for statement in statements:

                    if statement.strip():

                        connection.exec_driver_sql(
                            statement
                        )

                print(
                    f"[SUCCESS] Executed {filename}"
                )

        print("\nDatabase initialization completed!")

    finally:

        engine.dispose()


if __name__ == "__main__":

    initialize_database()
