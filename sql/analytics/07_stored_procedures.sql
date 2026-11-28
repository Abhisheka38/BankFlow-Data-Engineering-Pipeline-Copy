CREATE OR REPLACE PROCEDURE
analytics.refresh_materialized_views()

LANGUAGE plpgsql

AS $$

BEGIN

    -- Coordinate with the Silver loading pipeline
    PERFORM pg_advisory_xact_lock(42001);

    REFRESH MATERIALIZED VIEW
        analytics.mv_branch_performance;

    REFRESH MATERIALIZED VIEW
        analytics.mv_customer_360;

    RAISE NOTICE
        'BankFlow materialized views refreshed successfully';

END;

$$;