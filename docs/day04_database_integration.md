# Day 04 – PostgreSQL Database Integration

## Objective

Integrate PostgreSQL with the BankFlow data engineering platform and implement an automated loading pipeline that transfers validated Silver Parquet datasets into a relational database.

## Technologies

- PostgreSQL
- Python
- Pandas
- SQLAlchemy
- Psycopg
- PyArrow
- Python-dotenv
- Pytest
- DBeaver

## Database Design

The BankFlow database contains a Silver schema with six relational banking tables:

- Branches
- Customers
- Accounts
- Transactions
- Loans
- Payments

An additional load_history table stores successful pipeline execution metadata.

## Data Integrity

The database implements:

- Primary key constraints
- Foreign key constraints
- NOT NULL constraints
- CHECK constraints
- Exact decimal storage for financial amounts
- Database indexes

## Loading Strategy

The pipeline uses transactional full-refresh loading. Validated Silver Parquet files are read using Pandas, converted into database-compatible data types and loaded in dependency order.

All six banking tables are refreshed within a single PostgreSQL transaction. If any operation fails, uncommitted changes are rolled back.

## Data Lineage

The load history table records:

- Source Silver batch
- Source Bronze batch
- Database loading timestamp
- Total records loaded
- Per-table record counts
- Successful loading status

## Validation and Testing

Database validation checks record counts, primary keys, foreign key relationships, financial business rules and batch metadata.

Unit and integration tests cover decimal conversion, database connectivity and transactional rollback.

## Execution

1. `python -m src.database.connection`
2. `python -m src.database.init_db`
3. `python -m src.loading.load_silver`
4. `python -m src.validation.validate_database`
5. `python -m pytest tests/ -v`

## Current Limitations

The implementation uses a local PostgreSQL database and full-refresh snapshot loading. Incremental loading, change data capture, production-scale bulk loading, schema migrations and centralized monitoring are planned for future development.

## Next Steps

Implement advanced SQL transformations, common table expressions, window functions, analytical views and query performance analysis.