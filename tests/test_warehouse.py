
import pytest

from sqlalchemy import text

from src.database.connection import get_engine

from src.validation.validate_warehouse import CHECKS


@pytest.fixture(scope="module")
def engine():

    database_engine = get_engine()

    yield database_engine

    database_engine.dispose()


@pytest.mark.parametrize(

    "check_name, query",

    list(CHECKS.items()),

    ids=list(CHECKS.keys())

)
def test_warehouse_quality(

    engine,
    check_name,
    query

):

    with engine.begin() as connection:

        connection.execute(text(
            "SELECT pg_advisory_xact_lock(42001)"
        ))

        result = connection.execute(
            text(query)
        ).scalar_one()

        assert result is True, (
            f"Warehouse check failed: {check_name}"
        )


def test_dimension_tables_exist(engine):

    expected = {

        "dim_date",

        "dim_customer",

        "dim_branch",

        "dim_account",

        "dim_loan"

    }

    with engine.connect() as connection:

        rows = connection.execute(text("""

            SELECT tablename

            FROM pg_tables

            WHERE schemaname = 'warehouse'

        """)).fetchall()

        actual = {row[0] for row in rows}

        assert expected.issubset(actual)


def test_fact_tables_exist(engine):

    expected = {

        "fact_transactions",

        "fact_payments",

        "fact_account_snapshot",

        "fact_loan_snapshot"

    }

    with engine.connect() as connection:

        rows = connection.execute(text("""

            SELECT tablename

            FROM pg_tables

            WHERE schemaname = 'warehouse'

        """)).fetchall()

        actual = {row[0] for row in rows}

        assert expected.issubset(actual)


def test_customer_surrogate_key(engine):

    with engine.connect() as connection:

        result = connection.execute(text("""

            SELECT

                COUNT(*) =
                    COUNT(DISTINCT customer_key)

                AND

                COUNT(*) =
                    COUNT(DISTINCT customer_id)

            FROM warehouse.dim_customer

        """)).scalar_one()

        assert result is True


def test_account_snapshot_grain(engine):

    with engine.connect() as connection:

        result = connection.execute(text("""

            SELECT NOT EXISTS (

                SELECT date_key, account_key

                FROM warehouse.fact_account_snapshot

                GROUP BY date_key, account_key

                HAVING COUNT(*) > 1

            )

        """)).scalar_one()

        assert result is True


def test_loan_snapshot_grain(engine):

    with engine.connect() as connection:

        result = connection.execute(text("""

            SELECT NOT EXISTS (

                SELECT date_key, loan_key

                FROM warehouse.fact_loan_snapshot

                GROUP BY date_key, loan_key

                HAVING COUNT(*) > 1

            )

        """)).scalar_one()

        assert result is True


def test_warehouse_foreign_keys(engine):

    with engine.connect() as connection:

        result = connection.execute(text("""

            SELECT COUNT(*)

            FROM information_schema.table_constraints

            WHERE table_schema = 'warehouse'

            AND constraint_type = 'FOREIGN KEY'

            AND table_name IN (

                'fact_transactions',

                'fact_payments',

                'fact_account_snapshot',

                'fact_loan_snapshot'

            )

        """)).scalar_one()

        assert result == 16


def test_warehouse_load_history(engine):

    with engine.connect() as connection:

        result = connection.execute(text("""

            SELECT EXISTS (

                SELECT 1

                FROM warehouse.load_history

                WHERE status = 'success'

            )

        """)).scalar_one()

        assert result is True
