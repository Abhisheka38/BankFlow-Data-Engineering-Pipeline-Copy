# Day 6 – Data Warehousing and Dimensional Modelling

## Objective

Design and implement a dimensional banking data warehouse on top of validated PostgreSQL Silver datasets to support scalable analytical processing and future business intelligence reporting.

## Technologies Used

- PostgreSQL
- SQL
- Python
- SQLAlchemy
- Psycopg
- Pytest
- DBeaver

## Warehouse Architecture

Implemented a dedicated warehouse schema using dimensional modelling principles.

The warehouse uses a fact constellation architecture with shared dimensions across multiple banking business processes.

## Dimension Tables

| Dimension | Description |
|---|---|
| dim_date | Calendar and time-based analytical attributes |
| dim_customer | Customer demographic and profile information |
| dim_branch | Branch and geographical information |
| dim_account | Account descriptive attributes |
| dim_loan | Loan descriptive attributes |

## Fact Tables

| Fact Table | Grain |
|---|---|
| fact_transactions | One row per transaction |
| fact_payments | One row per loan payment |
| fact_account_snapshot | One row per account in the current snapshot |
| fact_loan_snapshot | One row per loan in the current snapshot |

## Dimensional Modelling Features

- Natural and surrogate keys
- Explicit fact table grain
- Conformed dimensions
- Star schema and fact constellation modelling
- Automatically generated date dimension
- Slowly Changing Dimension Type 1 using PostgreSQL UPSERT
- Surrogate key lookups
- Fact-to-dimension referential integrity

## Warehouse Loading

Implemented an automated SQL-based warehouse loading pipeline using Python and SQLAlchemy.

The loading process includes:

- Silver source validation
- Source load metadata verification
- Transactional dimension and fact loading
- Dimension UPSERT operations
- Full-refresh fact loading
- Record count reconciliation
- Transaction rollback on failure
- Warehouse load history and source lineage

## Data Quality

Implemented 20 warehouse validation rules covering:

- Dimension coverage
- Date dimension continuity
- Fact record reconciliation
- Grain uniqueness
- Financial reconciliation
- Transaction dimension mapping
- Silver-to-warehouse lineage

## Automated Testing

Implemented 27 warehouse integration test cases using Pytest.

## Analytical Queries

Implemented dimensional queries for:

- Monthly transaction volume
- Branch-level account portfolios
- Customer age group analysis
- Loan portfolio analysis
- Monthly loan payment analysis
- OLAP aggregation using ROLLUP

## Current Limitations

- Dimension attributes use SCD Type 1 rather than historical SCD Type 2.
- Fact tables use transactional full-refresh loading.
- Account and loan snapshots represent the current processing snapshot rather than historical daily balances.
- Financial measures are based on synthetic banking data.

## Next Steps

Implement the Gold layer, reusable business KPIs, reporting data marts, and analytical datasets for Power BI.