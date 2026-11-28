CREATE TABLE IF NOT EXISTS warehouse.dim_date (

    date_key INTEGER PRIMARY KEY,

    full_date DATE NOT NULL UNIQUE,

    day_of_month SMALLINT NOT NULL,

    day_name VARCHAR(15) NOT NULL,

    day_of_week SMALLINT NOT NULL,

    week_of_year SMALLINT NOT NULL,

    iso_year INTEGER NOT NULL,

    month_number SMALLINT NOT NULL,

    month_name VARCHAR(15) NOT NULL,

    quarter_number SMALLINT NOT NULL,

    calendar_year INTEGER NOT NULL,

    is_weekend BOOLEAN NOT NULL,

    CHECK (month_number BETWEEN 1 AND 12),

    CHECK (quarter_number BETWEEN 1 AND 4),

    CHECK (day_of_week BETWEEN 1 AND 7)

);

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (

    customer_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    customer_id VARCHAR(20) NOT NULL UNIQUE,

    full_name TEXT NOT NULL,

    gender VARCHAR(30),

    date_of_birth DATE NOT NULL,

    customer_age SMALLINT NOT NULL,

    age_group VARCHAR(30) NOT NULL,

    city VARCHAR(100),

    occupation VARCHAR(100),

    registration_date DATE NOT NULL,

    customer_status VARCHAR(30) NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS warehouse.dim_branch (

    branch_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    branch_id VARCHAR(20) NOT NULL UNIQUE,

    branch_name VARCHAR(150) NOT NULL,

    city VARCHAR(100) NOT NULL,

    district VARCHAR(100) NOT NULL,

    province VARCHAR(100) NOT NULL,

    opened_date DATE NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS warehouse.dim_account (

    account_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    account_id VARCHAR(20) NOT NULL UNIQUE,

    account_type VARCHAR(50) NOT NULL,

    currency VARCHAR(3) NOT NULL,

    opened_date DATE NOT NULL,

    account_status VARCHAR(30) NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS warehouse.dim_loan (

    loan_key BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    loan_id VARCHAR(20) NOT NULL UNIQUE,

    loan_type VARCHAR(50) NOT NULL,

    term_months INTEGER NOT NULL,

    loan_date DATE NOT NULL,

    maturity_date DATE NOT NULL,

    loan_status VARCHAR(30) NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP

);