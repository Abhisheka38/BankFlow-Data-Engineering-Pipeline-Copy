-- Materialized branch performance

CREATE MATERIALIZED VIEW IF NOT EXISTS
analytics.mv_branch_performance AS

SELECT *
FROM analytics.v_branch_performance

WITH DATA;


-- Materialized customer financial summary

CREATE MATERIALIZED VIEW IF NOT EXISTS
analytics.mv_customer_360 AS

SELECT *
FROM analytics.v_customer_360

WITH DATA;


-- Unique indexes

CREATE UNIQUE INDEX IF NOT EXISTS
idx_mv_branch_performance_branch

ON analytics.mv_branch_performance (
    branch_id
);


CREATE UNIQUE INDEX IF NOT EXISTS
idx_mv_customer_360_customer

ON analytics.mv_customer_360 (
    customer_id
);
