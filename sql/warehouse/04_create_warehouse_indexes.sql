-- Transaction fact indexes

CREATE INDEX IF NOT EXISTS idx_fact_txn_date
ON warehouse.fact_transactions(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_txn_customer
ON warehouse.fact_transactions(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_txn_account
ON warehouse.fact_transactions(account_key);

CREATE INDEX IF NOT EXISTS idx_fact_txn_branch_date
ON warehouse.fact_transactions(branch_key, date_key);


-- Payment fact indexes

CREATE INDEX IF NOT EXISTS idx_fact_payment_date
ON warehouse.fact_payments(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_payment_loan
ON warehouse.fact_payments(loan_key);

CREATE INDEX IF NOT EXISTS idx_fact_payment_customer
ON warehouse.fact_payments(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_payment_branch
ON warehouse.fact_payments(branch_key);


-- Account snapshot indexes

CREATE INDEX IF NOT EXISTS idx_account_snapshot_customer
ON warehouse.fact_account_snapshot(customer_key);

CREATE INDEX IF NOT EXISTS idx_account_snapshot_branch
ON warehouse.fact_account_snapshot(branch_key);

CREATE INDEX IF NOT EXISTS idx_account_snapshot_account
ON warehouse.fact_account_snapshot(account_key);


-- Loan snapshot indexes

CREATE INDEX IF NOT EXISTS idx_loan_snapshot_customer
ON warehouse.fact_loan_snapshot(customer_key);

CREATE INDEX IF NOT EXISTS idx_loan_snapshot_branch
ON warehouse.fact_loan_snapshot(branch_key);

CREATE INDEX IF NOT EXISTS idx_loan_snapshot_loan
ON warehouse.fact_loan_snapshot(loan_key);


-- Date dimension index

CREATE INDEX IF NOT EXISTS idx_dim_date_year_month
ON warehouse.dim_date(calendar_year, month_number);