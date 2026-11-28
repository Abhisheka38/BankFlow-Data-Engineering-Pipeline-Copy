TRUNCATE TABLE

    warehouse.fact_transactions,

    warehouse.fact_payments,

    warehouse.fact_account_snapshot,

    warehouse.fact_loan_snapshot

RESTART IDENTITY;

INSERT INTO warehouse.fact_transactions (

    transaction_id,
    date_key,
    customer_key,
    account_key,
    branch_key,
    transaction_timestamp,
    transaction_type,
    transaction_status,
    channel,
    currency,
    amount,
    signed_amount,
    realized_amount,
    transaction_count

)

SELECT

    t.transaction_id,

    dd.date_key,

    dc.customer_key,

    da.account_key,

    db.branch_key,

    t.transaction_timestamp,

    t.transaction_type,

    t.transaction_status,

    t.channel,

    t.currency,

    t.amount,

    t.signed_amount,

    t.realized_amount,

    1

FROM silver.transactions t

JOIN silver.accounts a
    ON t.account_id = a.account_id

JOIN warehouse.dim_account da
    ON t.account_id = da.account_id

JOIN warehouse.dim_customer dc
    ON a.customer_id = dc.customer_id

JOIN warehouse.dim_branch db
    ON t.branch_id = db.branch_id

JOIN warehouse.dim_date dd
    ON t.transaction_date = dd.full_date;

INSERT INTO warehouse.fact_payments (

    payment_id,
    date_key,
    loan_key,
    customer_key,
    branch_key,
    payment_method,
    payment_status,
    amount_paid,
    realized_payment_amount,
    payment_count

)

SELECT

    p.payment_id,

    dd.date_key,

    dl.loan_key,

    dc.customer_key,

    db.branch_key,

    p.payment_method,

    p.payment_status,

    p.amount_paid,

    p.realized_payment_amount,

    1

FROM silver.payments p

JOIN silver.loans l
    ON p.loan_id = l.loan_id

JOIN warehouse.dim_loan dl
    ON p.loan_id = dl.loan_id

JOIN warehouse.dim_customer dc
    ON l.customer_id = dc.customer_id

JOIN warehouse.dim_branch db
    ON l.branch_id = db.branch_id

JOIN warehouse.dim_date dd
    ON p.payment_date = dd.full_date;

INSERT INTO warehouse.fact_account_snapshot (

    date_key,
    account_key,
    customer_key,
    branch_key,
    current_balance,
    balance_category,
    account_count

)

SELECT

    dd.date_key,

    da.account_key,

    dc.customer_key,

    db.branch_key,

    a.current_balance,

    a.balance_category,

    1

FROM silver.accounts a

JOIN warehouse.dim_account da
    ON a.account_id = da.account_id

JOIN warehouse.dim_customer dc
    ON a.customer_id = dc.customer_id

JOIN warehouse.dim_branch db
    ON a.branch_id = db.branch_id

JOIN warehouse.dim_date dd
    ON dd.full_date = CURRENT_DATE;

WITH payment_summary AS (

    SELECT

        loan_id,

        SUM(realized_payment_amount)
            AS total_realized_payments

    FROM silver.payments

    GROUP BY loan_id

)

INSERT INTO warehouse.fact_loan_snapshot (

    date_key,
    loan_key,
    customer_key,
    branch_key,
    principal_amount,
    annual_interest_rate,
    total_realized_payments,
    loan_count

)

SELECT

    dd.date_key,

    dl.loan_key,

    dc.customer_key,

    db.branch_key,

    l.principal_amount,

    l.annual_interest_rate,

    COALESCE(p.total_realized_payments, 0),

    1

FROM silver.loans l

JOIN warehouse.dim_loan dl
    ON l.loan_id = dl.loan_id

JOIN warehouse.dim_customer dc
    ON l.customer_id = dc.customer_id

JOIN warehouse.dim_branch db
    ON l.branch_id = db.branch_id

JOIN warehouse.dim_date dd
    ON dd.full_date = CURRENT_DATE

LEFT JOIN payment_summary p
    ON l.loan_id = p.loan_id;