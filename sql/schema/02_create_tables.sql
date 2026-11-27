
-- ==================================================
-- BANKFLOW SILVER DATABASE TABLES
-- ==================================================


-- 1. BRANCHES

CREATE TABLE IF NOT EXISTS silver.branches (

    branch_id VARCHAR(20) PRIMARY KEY,

    branch_name TEXT NOT NULL,

    city TEXT NOT NULL,

    district TEXT NOT NULL,

    province TEXT NOT NULL,

    opened_date DATE NOT NULL
);


-- 2. CUSTOMERS

CREATE TABLE IF NOT EXISTS silver.customers (

    customer_id VARCHAR(20) PRIMARY KEY,

    first_name TEXT NOT NULL,

    last_name TEXT NOT NULL,

    date_of_birth DATE NOT NULL,

    gender TEXT,

    city TEXT,

    occupation TEXT,

    registration_date DATE NOT NULL,

    home_branch_id VARCHAR(20) NOT NULL,

    customer_status TEXT NOT NULL,

    full_name TEXT NOT NULL,

    customer_age SMALLINT NOT NULL,

    age_group TEXT NOT NULL,

    CONSTRAINT fk_customer_branch
        FOREIGN KEY (home_branch_id)
        REFERENCES silver.branches(branch_id),

    CONSTRAINT chk_customer_age
        CHECK (customer_age BETWEEN 0 AND 120),

    CONSTRAINT chk_customer_status
        CHECK (
            customer_status IN ('Active', 'Inactive')
        ),

    CONSTRAINT chk_registration_date
        CHECK (registration_date >= date_of_birth)
);


-- 3. ACCOUNTS

CREATE TABLE IF NOT EXISTS silver.accounts (

    account_id VARCHAR(20) PRIMARY KEY,

    customer_id VARCHAR(20) NOT NULL,

    branch_id VARCHAR(20) NOT NULL,

    account_type TEXT NOT NULL,

    currency VARCHAR(3) NOT NULL,

    opened_date DATE NOT NULL,

    current_balance NUMERIC(18,2) NOT NULL,

    account_status TEXT NOT NULL,

    balance_category TEXT NOT NULL,

    CONSTRAINT fk_account_customer
        FOREIGN KEY (customer_id)
        REFERENCES silver.customers(customer_id),

    CONSTRAINT fk_account_branch
        FOREIGN KEY (branch_id)
        REFERENCES silver.branches(branch_id),

    CONSTRAINT chk_account_balance
        CHECK (current_balance >= 0),

    CONSTRAINT chk_account_type
        CHECK (
            account_type IN (
                'Savings',
                'Current',
                'Fixed Deposit'
            )
        ),

    CONSTRAINT chk_account_status
        CHECK (
            account_status IN (
                'Active',
                'Inactive',
                'Closed'
            )
        ),

    CONSTRAINT chk_account_currency
        CHECK (currency = 'LKR')
);


-- 4. TRANSACTIONS

CREATE TABLE IF NOT EXISTS silver.transactions (

    transaction_id VARCHAR(20) PRIMARY KEY,

    account_id VARCHAR(20) NOT NULL,

    branch_id VARCHAR(20) NOT NULL,

    transaction_timestamp TIMESTAMP NOT NULL,

    transaction_type TEXT NOT NULL,

    amount NUMERIC(18,2) NOT NULL,

    currency VARCHAR(3) NOT NULL,

    channel TEXT NOT NULL,

    transaction_status TEXT NOT NULL,

    description TEXT,

    transaction_date DATE NOT NULL,

    transaction_year INTEGER NOT NULL,

    transaction_month SMALLINT NOT NULL,

    signed_amount NUMERIC(18,2) NOT NULL,

    realized_amount NUMERIC(18,2) NOT NULL,

    CONSTRAINT fk_transaction_account
        FOREIGN KEY (account_id)
        REFERENCES silver.accounts(account_id),

    CONSTRAINT fk_transaction_branch
        FOREIGN KEY (branch_id)
        REFERENCES silver.branches(branch_id),

    CONSTRAINT chk_transaction_amount
        CHECK (amount > 0),

    CONSTRAINT chk_transaction_type
        CHECK (
            transaction_type IN ('Credit', 'Debit')
        ),

    CONSTRAINT chk_transaction_status
        CHECK (
            transaction_status IN (
                'Successful',
                'Pending',
                'Failed'
            )
        ),

    CONSTRAINT chk_transaction_currency
        CHECK (currency = 'LKR'),

    CONSTRAINT chk_transaction_month
        CHECK (transaction_month BETWEEN 1 AND 12),

    CONSTRAINT chk_transaction_channel
        CHECK (
            channel IN (
                'ATM',
                'Mobile Banking',
                'Online Banking',
                'Branch'
            )
        ),

    CONSTRAINT chk_signed_amount
        CHECK (
            signed_amount =
                CASE
                    WHEN transaction_type = 'Credit'
                    THEN amount
                    ELSE -amount
                END
        ),

    CONSTRAINT chk_realized_amount
        CHECK (
            realized_amount =
                CASE
                    WHEN transaction_status = 'Successful'
                    THEN signed_amount
                    ELSE 0
                END
        )
);


-- 5. LOANS

CREATE TABLE IF NOT EXISTS silver.loans (

    loan_id VARCHAR(20) PRIMARY KEY,

    customer_id VARCHAR(20) NOT NULL,

    branch_id VARCHAR(20) NOT NULL,

    loan_type TEXT NOT NULL,

    principal_amount NUMERIC(18,2) NOT NULL,

    annual_interest_rate NUMERIC(5,2) NOT NULL,

    term_months INTEGER NOT NULL,

    loan_date DATE NOT NULL,

    loan_status TEXT NOT NULL,

    annual_interest_rate_decimal NUMERIC(7,6) NOT NULL,

    maturity_date DATE NOT NULL,

    CONSTRAINT fk_loan_customer
        FOREIGN KEY (customer_id)
        REFERENCES silver.customers(customer_id),

    CONSTRAINT fk_loan_branch
        FOREIGN KEY (branch_id)
        REFERENCES silver.branches(branch_id),

    CONSTRAINT chk_loan_principal
        CHECK (principal_amount > 0),

    CONSTRAINT chk_interest_rate
        CHECK (
            annual_interest_rate BETWEEN 0 AND 100
        ),

    CONSTRAINT chk_loan_term
        CHECK (
            term_months IN (12, 24, 36, 48, 60)
        ),

    CONSTRAINT chk_loan_type
        CHECK (
            loan_type IN (
                'Personal',
                'Housing',
                'Vehicle',
                'Business'
            )
        ),

    CONSTRAINT chk_loan_status
        CHECK (
            loan_status IN (
                'Active',
                'Closed',
                'Defaulted'
            )
        ),

    CONSTRAINT chk_maturity_date
        CHECK (maturity_date > loan_date),

    CONSTRAINT chk_interest_rate_decimal
        CHECK (
            annual_interest_rate_decimal =
                annual_interest_rate / 100
        )
);


-- 6. PAYMENTS

CREATE TABLE IF NOT EXISTS silver.payments (

    payment_id VARCHAR(20) PRIMARY KEY,

    loan_id VARCHAR(20) NOT NULL,

    payment_date DATE NOT NULL,

    amount_paid NUMERIC(18,2) NOT NULL,

    payment_method TEXT,

    payment_status TEXT NOT NULL,

    payment_year INTEGER NOT NULL,

    payment_month SMALLINT NOT NULL,

    realized_payment_amount NUMERIC(18,2) NOT NULL,

    CONSTRAINT fk_payment_loan
        FOREIGN KEY (loan_id)
        REFERENCES silver.loans(loan_id),

    CONSTRAINT chk_payment_amount
        CHECK (amount_paid > 0),

    CONSTRAINT chk_payment_status
        CHECK (
            payment_status IN (
                'Paid',
                'Pending',
                'Failed'
            )
        ),

    CONSTRAINT chk_payment_month
        CHECK (payment_month BETWEEN 1 AND 12),

    CONSTRAINT chk_realized_payment
        CHECK (
            realized_payment_amount =
                CASE
                    WHEN payment_status = 'Paid'
                    THEN amount_paid
                    ELSE 0
                END
        )
);


-- 7. PIPELINE LOAD HISTORY

CREATE TABLE IF NOT EXISTS silver.load_history (

    load_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    source_silver_batch TEXT NOT NULL,

    source_bronze_batch TEXT NOT NULL,

    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    total_records INTEGER NOT NULL,

    table_counts JSONB NOT NULL,

    status TEXT NOT NULL DEFAULT 'success',

    CONSTRAINT chk_total_records
        CHECK (total_records >= 0),

    CONSTRAINT chk_load_status
        CHECK (status = 'success')
);
