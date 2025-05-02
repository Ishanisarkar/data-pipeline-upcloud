# Lakehouse Project Architecture (FastAPI + dbt + DuckDB)

This repository implements a simplified local lakehouse architecture to ingest, store, transform, and serve data — inspired by production-grade patterns, but scoped for quick development and testing.

---

## Overall Architecture

```
           +----------------------+
           |   Raw Input (CSV)    |
           |  raw_input/warehouse |
           +----------+-----------+
                      |
                      v
         +------------+------------+
         |   FastAPI Ingestion     |  <-- See `data_preprocessing_ingestion/README.md`
         | - Reads and validates   |
         | - Writes partitioned    |
         |   Parquet (Hive-style)  |
         +------------+------------+
                      |
                      v
        +-------------+--------------+
        |  datawarehouse/default/    |  <-- Raw Parquet Lake
        |  billing/year=YYYY/...     |
        +-------------+--------------+
                      |
                      v
        +-------------+--------------+
        |  dbt + DuckDB (Models)     |  <-- See `README_dbt_duckdb_airflow.md`
        | - dbt run using DuckDB     |
        | - Materializes aggregates  |
        | - External Parquet output  |
        +-------------+--------------+
                      |
                      v
        datawarehouse/aggregates/{model}/date=YYYY-MM-DD/

```

---

## Data Flow (Implemented Components)

1. **Raw CSVs** are stored under:
   ```
   raw_input/warehouse/year=YYYY/month=MM/day=DD/billing.csv
   ```

2. **FastAPI**:
   - Validates the CSV schema
   - Converts types
   - Adds partition columns
   - Writes output as:
     ```
     datawarehouse/default/billing/year=YYYY/month=MM/day=DD/part-*.parquet
     ```

3. **dbt + DuckDB**:
   - Reads the preloaded `billing` table
   - Runs `dbt` models with external materializations
   - Outputs daily aggregates in:
     ```
     datawarehouse/aggregates/{model}/date=YYYY-MM-DD/
     ```

---

## Why DuckDB Instead of Trino?

In a production environment, we would use Trino or Spark + Iceberg for distributed compute and scale.  
However, for this scoped exercise (3 hours max), DuckDB is:
- ✅ Easier to set up (single binary, no cluster)
- ✅ Has native support for Parquet and SQL
- ✅ Works perfectly with dbt via `dbt-duckdb`
- ✅ Ideal for local lakehouse-style prototyping

---

## Subfolders and Purpose

| Folder                        | Description                                         |
|------------------------------|-----------------------------------------------------|
| `data_preprocessing_ingestion/` | FastAPI ingestion and schema validation             |
| `dbt_duckdb/`                | dbt models and configs using DuckDB as engine       |
| `duckdb/`                    | Contains `lakehouse.duckdb` database                |
| `datawarehouse/`             | Raw and aggregated Parquet outputs                  |

---

## See Also

- For ingestion logic and API usage → `data_preprocessing_ingestion/README.md`
- For dbt model usage, scheduling, and structure → `README_dbt_duckdb_airflow.md`

---

This architecture supports modular development and can easily be extended with Trino, Iceberg, or Airflow when moving beyond the 3-hour challenge scope.
