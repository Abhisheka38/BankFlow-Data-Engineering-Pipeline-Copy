# Day 02 – Data Generation, Bronze Ingestion and Validation

## Objective

Implement the initial batch data ingestion pipeline for BankFlow, an end-to-end banking data engineering and analytics platform.

## Data Sources

The project uses synthetic banking datasets generated using Python and Pandas. No actual customer or confidential banking data is used.

| Dataset | Records |
|---|---:|
| Branches | 20 |
| Customers | 1,000 |
| Accounts | 1,200 |
| Transactions | 10,000 |
| Loans | 500 |
| Payments | 3,000 |
| Total | 15,720 |

## Pipeline Components

- `generate_data.py`: Generates reproducible synthetic banking datasets.
- `ingest.py`: Validates source schemas, ingests original CSV files into the Bronze layer and generates ingestion metadata.
- `validate_bronze.py`: Validates primary keys, foreign keys, financial business rules, record counts and file integrity.

## Bronze Layer

Raw data is stored in timestamp-based ingestion batches.

Each successful batch contains six original CSV files and a JSON manifest.

## Data Engineering Features

- Batch data ingestion
- Schema validation
- Timestamp-based batch identification
- SHA-256 checksum verification
- Metadata management
- Primary and foreign key validation
- Business rule validation
- Incomplete batch cleanup
- Error handling

## Execution

1. `python src/ingestion/generate_data.py`
2. `python src/ingestion/ingest.py`
3. `python src/validation/validate_bronze.py`

## Testing

Test cases cover successful ingestion, missing source files, duplicate primary keys and recovery after restoring valid source data.

## Current Limitations

The pipeline uses local CSV files and synthetic data. It does not yet implement incremental ingestion, production-grade monitoring, comprehensive banking business rules or distributed processing.

## Next Steps

Implement the Silver layer for data cleaning, data type standardization, transformation and preparation for downstream analytics.