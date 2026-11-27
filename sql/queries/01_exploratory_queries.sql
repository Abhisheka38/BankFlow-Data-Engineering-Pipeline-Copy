
-- ==================================================
-- BANKFLOW EXPLORATORY SQL QUERIES
-- ==================================================


-- QUERY 1
-- Total number of customers

SELECT COUNT(*) AS total_customers
FROM silver.customers;


-- QUERY 2
-- Accounts by account type

SELECT
    account_type,
    COUNT(*) AS total_accounts
FROM silver.accounts
GROUP BY account_type
ORDER BY total_accounts DESC;


-- QUERY 3
-- Active account balances by account type

SELECT
    account_type,
    COUNT(*) AS active_accounts,
    SUM(current_balance) AS total_balance,
    ROUND(AVG(current_balance), 2) AS average_balance
FROM silver.accounts
WHERE account_status = 'Active'
GROUP BY account_type
ORDER BY total_balance DESC;


-- QUERY 4
-- Customers and their accounts

SELECT
    c.customer_id,
    c.full_name,
    a.account_id,
    a.account_type,
    a.current_balance
FROM silver.customers AS c
INNER JOIN silver.accounts AS a
    ON c.customer_id = a.customer_id
ORDER BY c.customer_id
LIMIT 20;


-- QUERY 5
-- Account balances by branch

SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    COUNT(a.account_id) AS total_accounts,
    COALESCE(
        SUM(a.current_balance),
        0
    ) AS total_balance
FROM silver.branches AS b
LEFT JOIN silver.accounts AS a
    ON b.branch_id = a.branch_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.city
ORDER BY total_balance DESC;


-- QUERY 6
-- Successful transaction volume by channel

SELECT
    channel,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_transaction_volume
FROM silver.transactions
WHERE transaction_status = 'Successful'
GROUP BY channel
ORDER BY total_transaction_volume DESC;


-- QUERY 7
-- Monthly net transaction flow

SELECT
    DATE_TRUNC(
        'month',
        transaction_timestamp
    )::DATE AS transaction_month,

    COUNT(*) AS successful_transactions,

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
    ) AS total_debits,

    SUM(realized_amount) AS net_flow

FROM silver.transactions

WHERE transaction_status = 'Successful'

GROUP BY
    DATE_TRUNC(
        'month',
        transaction_timestamp
    )

ORDER BY transaction_month;


-- QUERY 8
-- Loan principal by loan type

SELECT
    loan_type,
    COUNT(*) AS total_loans,
    SUM(principal_amount) AS total_principal,
    ROUND(
        AVG(annual_interest_rate),
        2
    ) AS average_interest_rate
FROM silver.loans
GROUP BY loan_type
ORDER BY total_principal DESC;


-- QUERY 9
-- Defaulted loan count percentage

SELECT
    COUNT(*) AS total_loans,

    COUNT(*) FILTER (
        WHERE loan_status = 'Defaulted'
    ) AS defaulted_loans,

    ROUND(

        100.0 * COUNT(*) FILTER (
            WHERE loan_status = 'Defaulted'
        )

        / NULLIF(COUNT(*), 0),

        2

    ) AS defaulted_loan_percentage

FROM silver.loans;


-- QUERY 10
-- Realized loan payments by loan

SELECT
    l.loan_id,
    l.loan_type,
    l.principal_amount,

    COALESCE(
        SUM(p.realized_payment_amount),
        0
    ) AS total_realized_payments

FROM silver.loans AS l

LEFT JOIN silver.payments AS p
    ON l.loan_id = p.loan_id

GROUP BY
    l.loan_id,
    l.loan_type,
    l.principal_amount

ORDER BY total_realized_payments DESC

LIMIT 20;
