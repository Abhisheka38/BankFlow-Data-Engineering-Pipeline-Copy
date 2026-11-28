-- Partial index for successful branch transactions

CREATE INDEX IF NOT EXISTS
idx_transactions_success_branch_date

ON silver.transactions (
    branch_id,
    transaction_date
)

WHERE transaction_status = 'Successful';


-- Index for latest successful account transactions

CREATE INDEX IF NOT EXISTS
idx_transactions_success_account_timestamp

ON silver.transactions (
    account_id,
    transaction_timestamp DESC,
    transaction_id DESC
)

WHERE transaction_status = 'Successful';


-- Index for active account portfolio queries

CREATE INDEX IF NOT EXISTS
idx_accounts_active_customer

ON silver.accounts (
    customer_id
)

WHERE account_status = 'Active';


-- Update PostgreSQL planner statistics

ANALYZE silver.transactions;
ANALYZE silver.accounts;
ANALYZE silver.customers;
ANALYZE silver.loans;
ANALYZE silver.payments;
ANALYZE silver.branches;