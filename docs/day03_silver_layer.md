# Day 03 – Data Cleaning and Silver Transformations

## Objective

Implement the Silver layer of the BankFlow data engineering platform by transforming raw Bronze banking datasets into cleaned, standardized, validated and enriched datasets.

## Data Sources

Six synthetic banking datasets from the Bronze layer:

- Branches
- Customers
- Accounts
- Transactions
- Loans
- Payments

## Data Profiling

The profiling module analyzes record counts, missing values, duplicate rows, data types and unique values. Profiling results are stored in JSON format.

## Data Cleaning

Reusable cleaning functions implement:

- Column name standardization
- Whitespace removal
- Identifier normalization
- Category standardization
- Numeric data type conversion
- Date conversion
- Exact duplicate removal
- Invalid record quarantine

## Banking Transformations

- Customer age calculation and age segmentation
- Customer full name generation
- Account balance categorization
- Transaction date, year and month extraction
- Signed transaction amount calculation
- Realized transaction amount calculation
- Loan maturity date calculation
- Interest rate decimal conversion
- Realized loan payment amount calculation

## Silver Storage

Clean datasets are stored in Apache Parquet format using PyArrow and Snappy compression.

Each Silver batch includes a JSON manifest containing source Bronze batch information, record counts, rejected record counts, removed duplicate counts, data types and file checksums.

## Data Quality

The pipeline implements primary key validation, foreign key validation, financial business rules, record reconciliation and file integrity verification.

Invalid records identified during Silver processing are stored in a quarantine directory with rejection reasons.

## Testing

Automated unit tests are implemented using Pytest to verify cleaning functions and banking transformations.

## Execution

Run the following commands from the project root:

`python -u src/preprocessing/profile_data.py`

`python -m src.transformation.run_silver`

`python -m src.validation.validate_silver`

`python -m pytest tests/test_clean_data.py -v`

## Limitations

The project uses synthetic banking data and simplified business rules. It does not yet implement production-grade financial precision, incremental processing, comprehensive temporal validation or distributed data processing.

## Next Steps

Implement relational database integration using PostgreSQL and SQL-based transformations for downstream banking analytics.