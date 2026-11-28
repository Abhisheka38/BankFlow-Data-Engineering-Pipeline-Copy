SELECT

    d.calendar_year,

    d.month_number,

    d.month_name,

    SUM(f.transaction_count)
        AS successful_transactions,

    SUM(f.amount)
        AS transaction_volume,

    SUM(f.realized_amount)
        AS net_transaction_flow

FROM warehouse.fact_transactions f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

WHERE f.transaction_status = 'Successful'

GROUP BY

    d.calendar_year,
    d.month_number,
    d.month_name

ORDER BY

    d.calendar_year,
    d.month_number;

SELECT

    b.branch_name,

    b.province,

    a.account_type,

    SUM(f.account_count)
        AS total_accounts,

    SUM(f.current_balance)
        AS total_balance

FROM warehouse.fact_account_snapshot f

JOIN warehouse.dim_branch b
    ON f.branch_key = b.branch_key

JOIN warehouse.dim_account a
    ON f.account_key = a.account_key

WHERE a.account_status = 'Active'

GROUP BY

    b.branch_name,
    b.province,
    a.account_type

ORDER BY total_balance DESC;

SELECT

    c.age_group,

    COUNT(DISTINCT f.customer_key)
        AS total_customers,

    SUM(f.account_count)
        AS total_accounts,

    SUM(f.current_balance)
        AS total_balance,

    ROUND(
        AVG(f.current_balance), 2
    ) AS average_account_balance

FROM warehouse.fact_account_snapshot f

JOIN warehouse.dim_customer c
    ON f.customer_key = c.customer_key

JOIN warehouse.dim_account a
    ON f.account_key = a.account_key

WHERE a.account_status = 'Active'

GROUP BY c.age_group

ORDER BY total_balance DESC;

SELECT

    b.province,

    l.loan_type,

    SUM(f.loan_count)
        AS total_loans,

    SUM(f.principal_amount)
        AS total_loan_principal,

    SUM(f.total_realized_payments)
        AS total_payments_received,

    ROUND(
        AVG(f.annual_interest_rate), 2
    ) AS average_interest_rate

FROM warehouse.fact_loan_snapshot f

JOIN warehouse.dim_branch b
    ON f.branch_key = b.branch_key

JOIN warehouse.dim_loan l
    ON f.loan_key = l.loan_key

GROUP BY

    b.province,
    l.loan_type

ORDER BY total_loan_principal DESC;

SELECT

    d.calendar_year,

    d.month_number,

    d.month_name,

    l.loan_type,

    SUM(f.payment_count)
        AS successful_payments,

    SUM(f.realized_payment_amount)
        AS total_payments_received

FROM warehouse.fact_payments f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_loan l
    ON f.loan_key = l.loan_key

WHERE f.payment_status = 'Paid'

GROUP BY

    d.calendar_year,
    d.month_number,
    d.month_name,
    l.loan_type

ORDER BY

    d.calendar_year,
    d.month_number,
    l.loan_type;

SELECT

    CASE
        WHEN GROUPING(b.province) = 1
        THEN 'All Provinces'
        ELSE b.province
    END AS province,

    CASE
        WHEN GROUPING(a.account_type) = 1
        THEN 'All Account Types'
        ELSE a.account_type
    END AS account_type,

    SUM(f.current_balance)
        AS total_balance

FROM warehouse.fact_account_snapshot f

JOIN warehouse.dim_branch b
    ON f.branch_key = b.branch_key

JOIN warehouse.dim_account a
    ON f.account_key = a.account_key

WHERE a.account_status = 'Active'

GROUP BY ROLLUP (

    b.province,
    a.account_type

)

ORDER BY

    GROUPING(b.province),

    b.province,

    GROUPING(a.account_type),

    a.account_type;

