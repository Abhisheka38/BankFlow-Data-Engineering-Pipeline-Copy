# Day 5 – Advanced SQL and Analytical Transformations

## Objective

Develop a reusable analytical processing layer on top of the BankFlow PostgreSQL Silver schema using advanced SQL transformations, analytical views, materialized views, stored procedures, query optimization, and automated data quality validation.

## Technologies Used

- PostgreSQL
- SQL
- Python
- SQLAlchemy
- Psycopg
- Pytest
- DBeaver (optional)

## Implementation

### Advanced SQL

- Implemented multi-table joins and correlated subqueries.
- Used Common Table Expressions to organize complex transformations.
- Applied conditional aggregation and date-based analysis.
- Implemented ROW_NUMBER, RANK, DENSE_RANK, LAG, NTILE, and running totals.
- Prevented financial aggregation errors caused by join fan-out.

### Analytical Views

Created five reusable analytical views:

| View | Purpose |
|---|---|
| v_customer_360 | Unified customer financial profile |
| v_branch_performance | Branch-level banking metrics |
| v_daily_transactions | Daily transaction activity |
| v_loan_portfolio | Loan portfolio analysis |
| v_account_portfolio | Account portfolio analysis |

### Materialized Views

Created materialized views for customer financial profiles and branch performance.

Implemented a stored procedure and Python refresh utility to update materialized views after Silver data loading.

### Query Optimization

- Implemented partial and composite indexes.
- Updated PostgreSQL planner statistics.
- Analyzed query execution plans using EXPLAIN ANALYZE and BUFFERS.
- Recorded before-and-after execution plans for performance evaluation.

### Data Quality

Implemented 15 analytical validation rules covering:

- Record counts
- Analytical grain uniqueness
- Financial reconciliation
- Transaction status reconciliation
- Materialized view consistency

### Automated Testing

Implemented 18 analytics integration test cases using Pytest, including parameterized data quality tests and database object existence checks.

## Business Value

The analytics layer provides reusable, consistent banking datasets for customer segmentation, branch performance monitoring, transaction analysis, account portfolio reporting, and loan portfolio reporting.

## Next Steps

Design a dimensional data warehouse with fact and dimension tables and implement the Gold analytical layer.