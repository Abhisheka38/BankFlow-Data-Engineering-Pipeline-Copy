INSERT INTO warehouse.dim_customer (

    customer_id,
    full_name,
    gender,
    date_of_birth,
    customer_age,
    age_group,
    city,
    occupation,
    registration_date,
    customer_status

)

SELECT

    customer_id,
    full_name,
    gender,
    date_of_birth,
    customer_age,
    age_group,
    city,
    occupation,
    registration_date,
    customer_status

FROM silver.customers

ON CONFLICT (customer_id)

DO UPDATE SET

    full_name = EXCLUDED.full_name,

    gender = EXCLUDED.gender,

    date_of_birth = EXCLUDED.date_of_birth,

    customer_age = EXCLUDED.customer_age,

    age_group = EXCLUDED.age_group,

    city = EXCLUDED.city,

    occupation = EXCLUDED.occupation,

    registration_date = EXCLUDED.registration_date,

    customer_status = EXCLUDED.customer_status,

    updated_at = CURRENT_TIMESTAMP;

    INSERT INTO warehouse.dim_branch (

    branch_id,
    branch_name,
    city,
    district,
    province,
    opened_date

)

SELECT

    branch_id,
    branch_name,
    city,
    district,
    province,
    opened_date

FROM silver.branches

ON CONFLICT (branch_id)

DO UPDATE SET

    branch_name = EXCLUDED.branch_name,

    city = EXCLUDED.city,

    district = EXCLUDED.district,

    province = EXCLUDED.province,

    opened_date = EXCLUDED.opened_date,

    updated_at = CURRENT_TIMESTAMP;

    INSERT INTO warehouse.dim_account (

    account_id,
    account_type,
    currency,
    opened_date,
    account_status

)

SELECT

    account_id,
    account_type,
    currency,
    opened_date,
    account_status

FROM silver.accounts

ON CONFLICT (account_id)

DO UPDATE SET

    account_type = EXCLUDED.account_type,

    currency = EXCLUDED.currency,

    opened_date = EXCLUDED.opened_date,

    account_status = EXCLUDED.account_status,

    updated_at = CURRENT_TIMESTAMP;

    INSERT INTO warehouse.dim_loan (

    loan_id,
    loan_type,
    term_months,
    loan_date,
    maturity_date,
    loan_status

)

SELECT

    loan_id,
    loan_type,
    term_months,
    loan_date,
    maturity_date,
    loan_status

FROM silver.loans

ON CONFLICT (loan_id)

DO UPDATE SET

    loan_type = EXCLUDED.loan_type,

    term_months = EXCLUDED.term_months,

    loan_date = EXCLUDED.loan_date,

    maturity_date = EXCLUDED.maturity_date,

    loan_status = EXCLUDED.loan_status,

    updated_at = CURRENT_TIMESTAMP;