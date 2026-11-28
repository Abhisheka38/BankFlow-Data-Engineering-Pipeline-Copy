CREATE TABLE IF NOT EXISTS warehouse.fact_transactions (

    transaction_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    transaction_id VARCHAR(20) NOT NULL UNIQUE,

    date_key INTEGER NOT NULL
        REFERENCES warehouse.dim_date(date_key),

    customer_key BIGINT NOT NULL
        REFERENCES warehouse.dim_customer(customer_key),

    account_key BIGINT NOT NULL
        REFERENCES warehouse.dim_account(account_key),

    branch_key BIGINT NOT NULL
        REFERENCES warehouse.dim_branch(branch_key),

    transaction_timestamp TIMESTAMP NOT NULL,

    transaction_type VARCHAR(30) NOT NULL,

    transaction_status VARCHAR(30) NOT NULL,

    channel VARCHAR(50) NOT NULL,

    currency VARCHAR(3) NOT NULL,

    amount NUMERIC(18,2) NOT NULL,

    signed_amount NUMERIC(18,2) NOT NULL,

    realized_amount NUMERIC(18,2) NOT NULL,

    transaction_count SMALLINT NOT NULL DEFAULT 1,

    CHECK (amount > 0),

    CHECK (transaction_count = 1),

    CHECK (
        transaction_type IN ('Credit', 'Debit')
    ),

    CHECK (
        signed_amount =
        CASE
            WHEN transaction_type = 'Credit'
            THEN amount
            ELSE -amount
        END
    ),

    CHECK (
        realized_amount =
        CASE
            WHEN transaction_status = 'Successful'
            THEN signed_amount
            ELSE 0
        END
    )

);

CREATE TABLE IF NOT EXISTS warehouse.fact_payments (

    payment_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    payment_id VARCHAR(20) NOT NULL UNIQUE,

    date_key INTEGER NOT NULL
        REFERENCES warehouse.dim_date(date_key),

    loan_key BIGINT NOT NULL
        REFERENCES warehouse.dim_loan(loan_key),

    customer_key BIGINT NOT NULL
        REFERENCES warehouse.dim_customer(customer_key),

    branch_key BIGINT NOT NULL
        REFERENCES warehouse.dim_branch(branch_key),

    payment_method VARCHAR(50),

    payment_status VARCHAR(30) NOT NULL,

    amount_paid NUMERIC(18,2) NOT NULL,

    realized_payment_amount NUMERIC(18,2) NOT NULL,

    payment_count SMALLINT NOT NULL DEFAULT 1,

    CHECK (amount_paid > 0),

    CHECK (payment_count = 1),

    CHECK (
        realized_payment_amount =
        CASE
            WHEN payment_status = 'Paid'
            THEN amount_paid
            ELSE 0
        END
    )

);

CREATE TABLE IF NOT EXISTS warehouse.fact_account_snapshot (

    snapshot_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    date_key INTEGER NOT NULL
        REFERENCES warehouse.dim_date(date_key),

    account_key BIGINT NOT NULL
        REFERENCES warehouse.dim_account(account_key),

    customer_key BIGINT NOT NULL
        REFERENCES warehouse.dim_customer(customer_key),

    branch_key BIGINT NOT NULL
        REFERENCES warehouse.dim_branch(branch_key),

    current_balance NUMERIC(18,2) NOT NULL,

    balance_category VARCHAR(30) NOT NULL,

    account_count SMALLINT NOT NULL DEFAULT 1,

    UNIQUE (date_key, account_key),

    CHECK (current_balance >= 0),

    CHECK (account_count = 1)

);

CREATE TABLE IF NOT EXISTS warehouse.fact_loan_snapshot (

    snapshot_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    date_key INTEGER NOT NULL
        REFERENCES warehouse.dim_date(date_key),

    loan_key BIGINT NOT NULL
        REFERENCES warehouse.dim_loan(loan_key),

    customer_key BIGINT NOT NULL
        REFERENCES warehouse.dim_customer(customer_key),

    branch_key BIGINT NOT NULL
        REFERENCES warehouse.dim_branch(branch_key),

    principal_amount NUMERIC(18,2) NOT NULL,

    annual_interest_rate NUMERIC(5,2) NOT NULL,

    total_realized_payments NUMERIC(20,2) NOT NULL,

    loan_count SMALLINT NOT NULL DEFAULT 1,

    UNIQUE (date_key, loan_key),

    CHECK (principal_amount > 0),

    CHECK (annual_interest_rate BETWEEN 0 AND 100),

    CHECK (total_realized_payments >= 0),

    CHECK (loan_count = 1)

);

CREATE TABLE IF NOT EXISTS warehouse.load_history (

    load_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    source_silver_load_id BIGINT NOT NULL
        REFERENCES silver.load_history(load_id),

    source_silver_batch TEXT NOT NULL,

    snapshot_date DATE NOT NULL,

    loaded_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    dimension_counts JSONB NOT NULL,

    fact_counts JSONB NOT NULL,

    status VARCHAR(20) NOT NULL
        DEFAULT 'success',

    CHECK (status = 'success')

);