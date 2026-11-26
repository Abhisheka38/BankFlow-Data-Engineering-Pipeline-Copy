# BankFlow-Data-Engineering-Pipeline-Copy
End-to-end banking data engineering pipeline using Python, Pandas, PostgreSQL, Apache Airflow, PySpark and Docker.

## Project Progress

### Day 01 – Project Setup

- GitHub repository initialization
- Python virtual environment configuration
- Project directory structure
- Dependency management
- Environment configuration

### Day 02 – Data Generation and Bronze Ingestion

- Generated six synthetic banking datasets containing 15,720 records.
- Implemented a Python-based batch ingestion pipeline.
- Implemented timestamp-based Bronze storage.
- Added source schema validation and ingestion metadata.
- Implemented SHA-256 file integrity verification.
- Implemented primary key, foreign key and financial business rule validation.
- Added failure handling for incomplete ingestion batches.

### Pipeline Architecture

Source CSV Files → Batch Ingestion → Bronze Layer → Data Quality Validation → Silver Layer (planned) → Gold Layer (planned)

### Technologies

Python, Pandas, JSON, CSV, SHA-256, Git and GitHub.

### Data Privacy

All banking data used in this project is synthetically generated. The project does not use real customer records or confidential banking information.

### Day 03 – Data Cleaning and Silver Transformations

- Implemented automated Bronze data profiling.
- Developed reusable data cleaning and standardization functions.
- Implemented banking-specific data transformations.
- Added customer segmentation and account balance categorization.
- Implemented signed and realized transaction amount calculations.
- Added loan maturity date and payment transformations.
- Converted cleaned CSV datasets into Apache Parquet format.
- Implemented invalid record quarantine and record reconciliation.
- Added Silver layer metadata and data lineage tracking.
- Implemented Silver data quality validation.
- Developed automated unit tests using Pytest.

**Technologies:** Python, Pandas, NumPy, PyArrow, Apache Parquet, JSON and Pytest.

**Architecture:**

Source Data → Bronze Ingestion → Data Profiling → Silver Transformations → Silver Validation → Gold Analytics (Planned)