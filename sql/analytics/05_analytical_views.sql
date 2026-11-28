CREATE OR REPLACE VIEW analytics.v_customer_360 AS

WITH account_summary AS (

    SELECT
        customer_id,
        COUNT(*) AS total_accounts,

        COUNT(*) FILTER (
            WHERE account_status = 'Active'
        ) AS active_accounts,

        SUM(current_balance) AS total_account_balance,

        COALESCE(
            SUM(current_balance) FILTER (
                WHERE account_status = 'Active'
            ), 0
        ) AS active_account_balance

    FROM silver.accounts
    GROUP BY customer_id

),

loan_summary AS (

    SELECT
        customer_id,
        COUNT(*) AS total_loans,

        COUNT(*) FILTER (
            WHERE loan_status = 'Active'
        ) AS active_loans,

        SUM(principal_amount) AS total_loan_principal

    FROM silver.loans
    GROUP BY customer_id

),

transaction_summary AS (

    SELECT
        a.customer_id,
        COUNT(*) AS successful_transactions,
        SUM(t.amount) AS transaction_volume,
        SUM(t.realized_amount) AS net_transaction_flow

    FROM silver.transactions t

    JOIN silver.accounts a
        ON t.account_id = a.account_id

    WHERE t.transaction_status = 'Successful'

    GROUP BY a.customer_id

)

SELECT
    c.customer_id,
    c.full_name,
    c.customer_age,
    c.age_group,
    c.city,
    c.occupation,
    c.customer_status,
    c.home_branch_id,

    COALESCE(a.total_accounts, 0) AS total_accounts,
    COALESCE(a.active_accounts, 0) AS active_accounts,

    COALESCE(a.total_account_balance, 0)
        AS total_account_balance,

    COALESCE(a.active_account_balance, 0)
        AS active_account_balance,

    COALESCE(l.total_loans, 0) AS total_loans,
    COALESCE(l.active_loans, 0) AS active_loans,

    COALESCE(l.total_loan_principal, 0)
        AS total_loan_principal,

    COALESCE(t.successful_transactions, 0)
        AS successful_transactions,

    COALESCE(t.transaction_volume, 0)
        AS transaction_volume,

    COALESCE(t.net_transaction_flow, 0)
        AS net_transaction_flow

FROM silver.customers c

LEFT JOIN account_summary a
    ON c.customer_id = a.customer_id

LEFT JOIN loan_summary l
    ON c.customer_id = l.customer_id

LEFT JOIN transaction_summary t
    ON c.customer_id = t.customer_id;

CREATE OR REPLACE VIEW analytics.v_branch_performance AS

WITH customer_summary AS (

    SELECT
        home_branch_id AS branch_id,
        COUNT(*) AS registered_customers
    FROM silver.customers
    GROUP BY home_branch_id

),

account_summary AS (

    SELECT
        branch_id,
        COUNT(*) AS total_accounts,

        COUNT(*) FILTER (
            WHERE account_status = 'Active'
        ) AS active_accounts,

        SUM(current_balance) AS total_account_balance

    FROM silver.accounts
    GROUP BY branch_id

),

transaction_summary AS (

    SELECT
        branch_id,
        COUNT(*) AS successful_transactions,
        SUM(amount) AS transaction_volume,
        SUM(realized_amount) AS net_transaction_flow

    FROM silver.transactions
    WHERE transaction_status = 'Successful'
    GROUP BY branch_id

),

loan_summary AS (

    SELECT
        branch_id,
        COUNT(*) AS total_loans,
        SUM(principal_amount) AS total_loan_principal,

        COUNT(*) FILTER (
            WHERE loan_status = 'Defaulted'
        ) AS defaulted_loans

    FROM silver.loans
    GROUP BY branch_id

)

SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    b.district,
    b.province,

    COALESCE(c.registered_customers, 0)
        AS registered_customers,

    COALESCE(a.total_accounts, 0)
        AS total_accounts,

    COALESCE(a.active_accounts, 0)
        AS active_accounts,

    COALESCE(a.total_account_balance, 0)
        AS total_account_balance,

    COALESCE(t.successful_transactions, 0)
        AS successful_transactions,

    COALESCE(t.transaction_volume, 0)
        AS transaction_volume,

    COALESCE(t.net_transaction_flow, 0)
        AS net_transaction_flow,

    COALESCE(l.total_loans, 0)
        AS total_loans,

    COALESCE(l.total_loan_principal, 0)
        AS total_loan_principal,

    COALESCE(l.defaulted_loans, 0)
        AS defaulted_loans

FROM silver.branches b

LEFT JOIN customer_summary c
    ON b.branch_id = c.branch_id

LEFT JOIN account_summary a
    ON b.branch_id = a.branch_id

LEFT JOIN transaction_summary t
    ON b.branch_id = t.branch_id

LEFT JOIN loan_summary l
    ON b.branch_id = l.branch_id;

CREATE OR REPLACE VIEW analytics.v_daily_transactions AS

SELECT
    transaction_date,
    branch_id,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE transaction_status = 'Successful'
    ) AS successful_transactions,

    COUNT(*) FILTER (
        WHERE transaction_status = 'Failed'
    ) AS failed_transactions,

    COUNT(*) FILTER (
        WHERE transaction_status = 'Pending'
    ) AS pending_transactions,

    COALESCE(
        SUM(amount) FILTER (
            WHERE transaction_type = 'Credit'
            AND transaction_status = 'Successful'
        ), 0
    ) AS total_credits,

    COALESCE(
        SUM(amount) FILTER (
            WHERE transaction_type = 'Debit'
            AND transaction_status = 'Successful'
        ), 0
    ) AS total_debits,

    SUM(realized_amount) AS net_transaction_flow

FROM silver.transactions

GROUP BY
    transaction_date,
    branch_id;

CREATE OR REPLACE VIEW analytics.v_loan_portfolio AS

SELECT
    branch_id,
    loan_type,

    COUNT(*) AS total_loans,

    COUNT(*) FILTER (
        WHERE loan_status = 'Active'
    ) AS active_loans,

    COUNT(*) FILTER (
        WHERE loan_status = 'Closed'
    ) AS closed_loans,

    COUNT(*) FILTER (
        WHERE loan_status = 'Defaulted'
    ) AS defaulted_loans,

    SUM(principal_amount) AS total_loan_principal,

    ROUND(
        AVG(annual_interest_rate), 2
    ) AS average_interest_rate,

    ROUND(
        COUNT(*) FILTER (
            WHERE loan_status = 'Defaulted'
        ) * 100.0
        / NULLIF(COUNT(*), 0),
        2
    ) AS defaulted_loan_percentage

FROM silver.loans

GROUP BY
    branch_id,
    loan_type;

 CREATE OR REPLACE VIEW analytics.v_account_portfolio AS

SELECT
    branch_id,
    account_type,

    COUNT(*) AS total_accounts,

    COUNT(*) FILTER (
        WHERE account_status = 'Active'
    ) AS active_accounts,

    COUNT(*) FILTER (
        WHERE account_status = 'Closed'
    ) AS closed_accounts,

    SUM(current_balance) AS total_balance,

    COALESCE(
        SUM(current_balance) FILTER (
            WHERE account_status = 'Active'
        ), 0
    ) AS active_balance,

    ROUND(
        AVG(current_balance), 2
    ) AS average_balance

FROM silver.accounts

GROUP BY
    branch_id,
    account_type;
       