
from decimal import Decimal

import pandas as pd
import pytest

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.database.connection import get_engine

from src.loading.load_silver import (
    to_decimal,
    prepare_dataframe
)


# --------------------------------------------------
# UNIT TESTS
# --------------------------------------------------

def test_decimal_conversion():

    result = to_decimal(
        1500.25,
        "0.01"
    )

    assert result == Decimal("1500.25")


def test_decimal_rounding():

    result = to_decimal(
        "10.125",
        "0.01"
    )

    assert result == Decimal("10.13")


def test_missing_decimal_value():

    result = to_decimal(
        None,
        "0.01"
    )

    assert result is None


def test_prepare_accounts():

    dataframe = pd.DataFrame({

        "account_id": ["ACC001"],

        "current_balance": [5000.50],

        "opened_date": ["2025-01-01"],

        "balance_category": pd.Categorical(
            ["Low"]
        )
    })

    result = prepare_dataframe(
        "accounts",
        dataframe
    )

    assert result.loc[
        0, "current_balance"
    ] == Decimal("5000.50")

    assert str(
        result.loc[0, "opened_date"]
    ) == "2025-01-01"

    assert result.loc[
        0, "balance_category"
    ] == "Low"


# --------------------------------------------------
# DATABASE INTEGRATION TESTS
# --------------------------------------------------

@pytest.fixture
def engine():

    database_engine = get_engine()

    yield database_engine

    database_engine.dispose()


def test_database_connection(engine):

    with engine.connect() as connection:

        result = connection.execute(

            text("SELECT 1")

        ).scalar_one()

    assert result == 1


def test_transaction_rollback(engine):

    # Use an isolated temporary table.
    # Do not modify the BankFlow banking tables.

    with engine.connect() as connection:

        connection.execute(

            text(
                """
                CREATE TEMP TABLE rollback_test (

                    id INTEGER PRIMARY KEY,

                    amount NUMERIC(10,2)
                        CHECK (amount > 0)
                )
                """
            )
        )

        connection.commit()

        # Save an initial valid record.
        connection.execute(

            text(
                """
                INSERT INTO rollback_test
                VALUES (1, 100)
                """
            )
        )

        connection.commit()

        # A failed transaction should restore
        # the previous committed contents.
        with pytest.raises(IntegrityError):

            with connection.begin():

                connection.execute(

                    text(
                        "TRUNCATE TABLE rollback_test"
                    )
                )

                connection.execute(

                    text(
                        """
                        INSERT INTO rollback_test
                        VALUES (2, 200)
                        """
                    )
                )

                # Intentional CHECK constraint violation.
                connection.execute(

                    text(
                        """
                        INSERT INTO rollback_test
                        VALUES (3, -500)
                        """
                    )
                )

        rows = connection.execute(

            text(
                """
                SELECT id, amount
                FROM rollback_test
                """
            )

        ).all()

        assert rows == [
            (1, Decimal("100.00"))
        ]

        connection.rollback()

        connection.execute(
            text("DROP TABLE rollback_test")
        )

        connection.commit()
