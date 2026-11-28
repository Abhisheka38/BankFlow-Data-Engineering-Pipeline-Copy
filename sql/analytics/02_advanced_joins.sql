SELECT
    c.customer_id,
    c.full_name,
    c.age_group,
    a.account_id,
    a.account_type,
    a.current_balance,
    a.account_status,
    b.branch_name,
    b.province
FROM silver.customers c
INNER JOIN silver.accounts a
    ON c.customer_id = a.customer_id
INNER JOIN silver.branches b
    ON a.branch_id = b.branch_id
ORDER BY c.customer_id
LIMIT 20;

SELECT
    c.customer_id,
    c.full_name,
    c.customer_status
FROM silver.customers c
LEFT JOIN silver.accounts a
    ON c.customer_id = a.customer_id
WHERE a.account_id IS NULL;

SELECT
    b.branch_id,
    b.branch_name,
    b.province,
    COUNT(a.account_id) AS total_accounts,
    COUNT(DISTINCT a.customer_id) AS total_customers,
    COALESCE(SUM(a.current_balance), 0) AS total_balance
FROM silver.branches b
LEFT JOIN silver.accounts a
    ON b.branch_id = a.branch_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.province
ORDER BY total_balance DESC;

SELECT
    c.customer_id,
    c.full_name
FROM silver.customers c
WHERE EXISTS (
    SELECT 1
    FROM silver.accounts a
    WHERE a.customer_id = c.customer_id
)
AND EXISTS (
    SELECT 1
    FROM silver.loans l
    WHERE l.customer_id = c.customer_id
);

SELECT
    l.loan_id,
    l.customer_id,
    l.loan_type,
    l.principal_amount,
    l.loan_status,
    COUNT(p.payment_id) AS payment_records,
    COUNT(p.payment_id) FILTER (
        WHERE p.payment_status = 'Paid'
    ) AS successful_payments,
    COALESCE(
        SUM(p.realized_payment_amount), 0
    ) AS total_realized_payments
FROM silver.loans l
LEFT JOIN silver.payments p
    ON l.loan_id = p.loan_id
GROUP BY
    l.loan_id,
    l.customer_id,
    l.loan_type,
    l.principal_amount,
    l.loan_status
ORDER BY total_realized_payments DESC
LIMIT 20;
