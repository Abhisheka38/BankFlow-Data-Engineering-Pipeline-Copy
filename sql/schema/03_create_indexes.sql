
-- Customer indexes

CREATE INDEX IF NOT EXISTS idx_customers_branch
ON silver.customers(home_branch_id);


-- Account indexes

CREATE INDEX IF NOT EXISTS idx_accounts_customer
ON silver.accounts(customer_id);

CREATE INDEX IF NOT EXISTS idx_accounts_branch
ON silver.accounts(branch_id);

CREATE INDEX IF NOT EXISTS idx_accounts_type
ON silver.accounts(account_type);


-- Transaction indexes

CREATE INDEX IF NOT EXISTS idx_transactions_account
ON silver.transactions(account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_branch
ON silver.transactions(branch_id);

CREATE INDEX IF NOT EXISTS idx_transactions_date
ON silver.transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_transactions_account_date
ON silver.transactions(
    account_id,
    transaction_date
);


-- Loan indexes

CREATE INDEX IF NOT EXISTS idx_loans_customer
ON silver.loans(customer_id);

CREATE INDEX IF NOT EXISTS idx_loans_branch
ON silver.loans(branch_id);

CREATE INDEX IF NOT EXISTS idx_loans_status
ON silver.loans(loan_status);


-- Payment indexes

CREATE INDEX IF NOT EXISTS idx_payments_loan
ON silver.payments(loan_id);

CREATE INDEX IF NOT EXISTS idx_payments_date
ON silver.payments(payment_date);
