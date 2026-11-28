
from sqlalchemy import text

from src.database.connection import get_engine


def refresh_analytics():

    engine = get_engine()

    print("\nRefreshing BankFlow analytics...\n")

    try:

        with engine.begin() as connection:

            connection.execute(
                text(
                    "CALL analytics."
                    "refresh_materialized_views()"
                )
            )

        print(
            "[SUCCESS] Materialized views refreshed."
        )

    except Exception:

        print(
            "[FAILED] Analytics refresh failed."
        )

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":

    refresh_analytics()
