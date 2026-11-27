
import os
from pathlib import Path

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# 2. CREATE DATABASE ENGINE
# --------------------------------------------------

def get_engine():

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD"
    ]

    missing = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing:

        raise ValueError(
            f"Missing environment variables: {missing}"
        )

    database_url = URL.create(

        drivername="postgresql+psycopg",

        username=os.getenv("DB_USER"),

        password=os.getenv("DB_PASSWORD"),

        host=os.getenv("DB_HOST"),

        port=int(os.getenv("DB_PORT")),

        database=os.getenv("DB_NAME")
    )

    engine = create_engine(

        database_url,

        pool_pre_ping=True,

        connect_args={
            "connect_timeout": 10
        }
    )

    return engine


# --------------------------------------------------
# 3. TEST DATABASE CONNECTION
# --------------------------------------------------

def test_connection():

    engine = get_engine()

    try:

        with engine.connect() as connection:

            result = connection.execute(

                text(
                    """
                    SELECT
                        current_database() AS database,
                        current_user AS username
                    """
                )
            )

            row = result.mappings().one()

            print(
                "PostgreSQL connection successful!"
            )

            print(
                f"Database: {row['database']}"
            )

            print(
                f"User: {row['username']}"
            )

    finally:

        engine.dispose()


if __name__ == "__main__":

    test_connection()
