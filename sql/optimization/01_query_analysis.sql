-- Query 1: Filter transactions by account

EXPLAIN (ANALYZE, BUFFERS)

SELECT
    transaction_id,
    account_id,
    amount,
    transaction_timestamp

FROM silver.transactions

WHERE account_id = 'ACC000001';


-- Query 2: Filter successful transactions

EXPLAIN (ANALYZE, BUFFERS)

SELECT
    branch_id,
    transaction_date,
    amount

FROM silver.transactions

WHERE transaction_status = 'Successful'
AND branch_id = 'BR0001'
AND transaction_date >= DATE '2024-01-01'
AND transaction_date < DATE '2025-01-01';


-- Query 3: Normal analytical view

EXPLAIN (ANALYZE, BUFFERS)

SELECT *
FROM analytics.v_branch_performance;


-- Query 4: Materialized analytical view

EXPLAIN (ANALYZE, BUFFERS)

SELECT *
FROM analytics.mv_branch_performance;


-- Query 5: Customer portfolio

EXPLAIN (ANALYZE, BUFFERS)

SELECT *
FROM analytics.v_customer_360
WHERE customer_id = 'CUST00001';