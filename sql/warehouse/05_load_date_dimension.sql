WITH date_bounds AS (

    SELECT

        LEAST(

            (SELECT MIN(opened_date)
             FROM silver.branches),

            (SELECT MIN(registration_date)
             FROM silver.customers),

            (SELECT MIN(opened_date)
             FROM silver.accounts),

            (SELECT MIN(transaction_date)
             FROM silver.transactions),

            (SELECT MIN(loan_date)
             FROM silver.loans),

            (SELECT MIN(payment_date)
             FROM silver.payments),

            CURRENT_DATE

        ) AS start_date,

        GREATEST(

            (SELECT MAX(transaction_date)
             FROM silver.transactions),

            (SELECT MAX(maturity_date)
             FROM silver.loans),

            (SELECT MAX(payment_date)
             FROM silver.payments),

            CURRENT_DATE

        ) AS end_date

),

calendar AS (

    SELECT

        GENERATE_SERIES(

            DATE_TRUNC('year', start_date),

            DATE_TRUNC('year', end_date)
                + INTERVAL '1 year'
                - INTERVAL '1 day',

            INTERVAL '1 day'

        )::DATE AS full_date

    FROM date_bounds

)

INSERT INTO warehouse.dim_date (

    date_key,
    full_date,
    day_of_month,
    day_name,
    day_of_week,
    week_of_year,
    iso_year,
    month_number,
    month_name,
    quarter_number,
    calendar_year,
    is_weekend

)

SELECT

    TO_CHAR(full_date, 'YYYYMMDD')::INTEGER,

    full_date,

    EXTRACT(DAY FROM full_date)::SMALLINT,

    TO_CHAR(full_date, 'FMDay'),

    EXTRACT(ISODOW FROM full_date)::SMALLINT,

    EXTRACT(WEEK FROM full_date)::SMALLINT,

    EXTRACT(ISOYEAR FROM full_date)::INTEGER,

    EXTRACT(MONTH FROM full_date)::SMALLINT,

    TO_CHAR(full_date, 'FMMonth'),

    EXTRACT(QUARTER FROM full_date)::SMALLINT,

    EXTRACT(YEAR FROM full_date)::INTEGER,

    EXTRACT(ISODOW FROM full_date) IN (6, 7)

FROM calendar

ON CONFLICT (date_key) DO NOTHING;