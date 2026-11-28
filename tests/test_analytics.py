
import pytest

from sqlalchemy import text

from src.database.connection import get_engine

from src.validation.validate_analytics import CHECKS


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
def test_analytics_quality(
    engine,
    check_name,
    query
):

    with engine.begin() as connection:

        connection.execute(
            text(
                "SELECT pg_advisory_xact_lock(42001)"
            )
        )

        result = connection.execute(
            text(query)
        ).scalar_one()

        assert result is True, (
            f"Analytics check failed: {check_name}"
        )


def test_analytics_views_exist(engine):

    expected_views = {
        "v_customer_360",
        "v_branch_performance",
        "v_daily_transactions",
        "v_loan_portfolio",
        "v_account_portfolio"
    }

    with engine.connect() as connection:

        rows = connection.execute(text("""
            SELECT viewname
            FROM pg_views
            WHERE schemaname = 'analytics'
        """)).fetchall()

        actual_views = {
            row[0] for row in rows
        }

        assert expected_views.issubset(
            actual_views
        )


def test_materialized_views_exist(engine):

    expected_views = {
        "mv_branch_performance",
        "mv_customer_360"
    }

    with engine.connect() as connection:

        rows = connection.execute(text("""
            SELECT matviewname
            FROM pg_matviews
            WHERE schemaname = 'analytics'
        """)).fetchall()

        actual_views = {
            row[0] for row in rows
        }

        assert expected_views.issubset(
            actual_views
        )


def test_refresh_procedure_exists(engine):

    with engine.connect() as connection:

        result = connection.execute(text("""
            SELECT EXISTS (

                SELECT 1

                FROM information_schema.routines

                WHERE routine_schema = 'analytics'

                AND routine_name =
                    'refresh_materialized_views'

                AND routine_type = 'PROCEDURE'
            )
        """)).scalar_one()

        assert result is True
