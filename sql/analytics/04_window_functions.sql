WITH ranked_transactions AS (

    SELECT
        transaction_id,
        account_id,
        transaction_timestamp,
        transaction_type,
        amount,

        ROW_NUMBER() OVER (
            PARTITION BY account_id
            ORDER BY
                transaction_timestamp DESC,
                transaction_id DESC
        ) AS row_num

    FROM silver.transactions

    WHERE transaction_status = 'Successful'

)

SELECT *
FROM ranked_transactions
WHERE row_num = 1
ORDER BY account_id
LIMIT 20;

WITH branch_balances AS (

    SELECT
        b.branch_id,
        b.branch_name,
        COALESCE(
            SUM(a.current_balance) FILTER (
                WHERE a.account_status = 'Active'
            ), 0
        ) AS total_balance

    FROM silver.branches b

    LEFT JOIN silver.accounts a
        ON b.branch_id = a.branch_id

    GROUP BY b.branch_id, b.branch_name

)

SELECT
    *,
    RANK() OVER (
        ORDER BY total_balance DESC
    ) AS branch_rank,

    DENSE_RANK() OVER (
        ORDER BY total_balance DESC
    ) AS dense_branch_rank

FROM branch_balances
ORDER BY branch_rank, branch_id;

SELECT
    account_id,
    transaction_id,
    transaction_timestamp,
    transaction_type,
    realized_amount,

    SUM(realized_amount) OVER (
        PARTITION BY account_id
        ORDER BY
            transaction_timestamp,
            transaction_id
        ROWS BETWEEN UNBOUNDED PRECEDING
        AND CURRENT ROW
    ) AS running_net_flow

FROM silver.transactions

WHERE transaction_status = 'Successful'

ORDER BY
    account_id,
    transaction_timestamp,
    transaction_id

LIMIT 50;
WITH monthly_volume AS (

    SELECT
        DATE_TRUNC(
            'month', transaction_date
        )::DATE AS month_start,

        SUM(amount) AS transaction_volume

    FROM silver.transactions

    WHERE transaction_status = 'Successful'

    GROUP BY 1

),

calendar AS (

    SELECT GENERATE_SERIES(
        MIN(month_start),
        MAX(month_start),
        INTERVAL '1 month'
    )::DATE AS month_start
    FROM monthly_volume

),

monthly_complete AS (

    SELECT
        c.month_start,
        COALESCE(m.transaction_volume, 0)
            AS transaction_volume
    FROM calendar c
    LEFT JOIN monthly_volume m
        ON c.month_start = m.month_start

),

monthly_comparison AS (

    SELECT
        month_start,
        transaction_volume,

        LAG(transaction_volume) OVER (
            ORDER BY month_start
        ) AS previous_month_volume

    FROM monthly_complete

)

SELECT
    month_start,
    transaction_volume,
    previous_month_volume,

    ROUND(
        (
            transaction_volume
            - previous_month_volume
        ) * 100.0
        / NULLIF(previous_month_volume, 0),
        2
    ) AS monthly_growth_percentage

FROM monthly_comparison

ORDER BY month_start;

WITH customer_balances AS (

    SELECT
        customer_id,
        SUM(current_balance) AS total_balance
    FROM silver.accounts
    WHERE account_status = 'Active'
    GROUP BY customer_id

)

SELECT
    customer_id,
    total_balance,

    NTILE(4) OVER (
        ORDER BY total_balance DESC, customer_id
    ) AS balance_quartile

FROM customer_balances

ORDER BY balance_quartile, total_balance DESC;
