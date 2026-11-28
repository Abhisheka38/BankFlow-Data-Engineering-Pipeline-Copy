WITH customer_balances AS (

    SELECT
        customer_id,
        SUM(current_balance) AS total_balance,
        COUNT(account_id) AS account_count
    FROM silver.accounts
    WHERE account_status = 'Active'
    GROUP BY customer_id

)

SELECT
    c.customer_id,
    c.full_name,
    cb.account_count,
    cb.total_balance
FROM customer_balances cb
JOIN silver.customers c
    ON cb.customer_id = c.customer_id
WHERE cb.total_balance >= 1000000
ORDER BY cb.total_balance DESC;
WITH customer_balances AS (

    SELECT
        c.customer_id,
        c.full_name,
        COALESCE(
            SUM(a.current_balance) FILTER (
                WHERE a.account_status = 'Active'
            ), 0
        ) AS total_balance
    FROM silver.customers c
    LEFT JOIN silver.accounts a
        ON c.customer_id = a.customer_id
    GROUP BY c.customer_id, c.full_name

),

customer_segments AS (

    SELECT
        *,
        CASE
            WHEN total_balance >= 1000000 THEN 'Premium'
            WHEN total_balance >= 500000 THEN 'Gold'
            WHEN total_balance >= 100000 THEN 'Silver'
            ELSE 'Standard'
        END AS customer_segment
    FROM customer_balances

)

SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    SUM(total_balance) AS segment_balance,
    ROUND(AVG(total_balance), 2) AS average_balance
FROM customer_segments
GROUP BY customer_segment
ORDER BY segment_balance DESC;
WITH monthly_transactions AS (

    SELECT
        DATE_TRUNC(
            'month', transaction_date
        )::DATE AS month_start,

        COUNT(*) AS transaction_count,

        SUM(
            CASE
                WHEN transaction_type = 'Credit'
                THEN amount
                ELSE 0
            END
        ) AS total_credits,

        SUM(
            CASE
                WHEN transaction_type = 'Debit'
                THEN amount
                ELSE 0
            END
        ) AS total_debits

    FROM silver.transactions

    WHERE transaction_status = 'Successful'

    GROUP BY 1

)

SELECT
    month_start,
    transaction_count,
    total_credits,
    total_debits,
    total_credits - total_debits AS net_flow
FROM monthly_transactions
ORDER BY month_start;

WITH account_summary AS (

    SELECT
        customer_id,
        COUNT(*) AS account_count,
        SUM(current_balance) AS total_balance
    FROM silver.accounts
    GROUP BY customer_id

),

loan_summary AS (

    SELECT
        customer_id,
        COUNT(*) AS loan_count,
        SUM(principal_amount) AS total_loan_principal
    FROM silver.loans
    GROUP BY customer_id

)

SELECT
    c.customer_id,
    c.full_name,
    COALESCE(a.account_count, 0) AS account_count,
    COALESCE(a.total_balance, 0) AS total_balance,
    COALESCE(l.loan_count, 0) AS loan_count,
    COALESCE(l.total_loan_principal, 0)
        AS total_loan_principal
FROM silver.customers c
LEFT JOIN account_summary a
    ON c.customer_id = a.customer_id
LEFT JOIN loan_summary l
    ON c.customer_id = l.customer_id
ORDER BY total_balance DESC
LIMIT 20;