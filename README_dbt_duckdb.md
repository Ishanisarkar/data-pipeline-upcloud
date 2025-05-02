# dbt + DuckDB + FastAPI Lakehouse Project

This project demonstrates a local lakehouse pattern using:
- **DuckDB** as the SQL execution engine (used instead of trino for ease)
- **dbt** for transformation and modeling
- **FastAPI** for ingestion and syncing with Iceberg or Trino
- **Makefile** for CLI-friendly execution
- **Airflow** (not implemented) for orchestration

---

## Input Data

Input files are CSVs stored in a partitioned structure:
```
raw_input/warehouse/year=YYYY/month=MM/day=DD/billing.csv
```
This file is big in size and cannot be uploaded to git. For the code to run smoothly, you will have to put billing.csv file in same hive partition format as you have sent me.
FastAPI reads these files, validates schema, and writes them as partitioned Parquet to:

```
datawarehouse/default/billing/year=YYYY/month=MM/day=DD/part-00000.parquet
```

---

## Output from dbt

dbt models process the raw data from the `billing` table and output aggregated results to:

```
datawarehouse/aggregates/{model}/date=YYYY-MM-DD/{model}.parquet
```

Examples:
- `daily_credit_usage`
- `failed_vs_success_per_user`

These outputs are used for reporting, analysis, and downstream syncing (e.g. with Trino).

---

## How to Run the dbt Project

### 1. Bootstrap: Create the `billing` table from Parquet
```bash
make bootstrap
```

### 2. Run all dbt models
```bash
make run
```

### 3. Run a specific model
```bash
make run_model model=daily_credit_usage
```

---

## How Airflow Would Call These

In Airflow, you would use a `BashOperator` or `PythonOperator` to call the Makefile or shell commands.

### Example: BashOperator
```python
from airflow.operators.bash import BashOperator

run_dbt_model = BashOperator(
    task_id="run_dbt_daily_credit",
    bash_command="make run_model_date model=daily_credit_usage target_date={{ ds }}",
    dag=dag,
)
```

### Example: PythonOperator
```python
from airflow.operators.python import PythonOperator

def run_model(**kwargs):
    import subprocess
    date = kwargs['ds']
    subprocess.run(["make", "run_model_date", f"model=daily_credit_usage", f"target_date={date}"], check=True)

task = PythonOperator(
    task_id="run_dbt_model_python",
    python_callable=run_model,
    provide_context=True,
    dag=dag,
)
```

This allows you to fully automate dbt model execution and ensure output is generated daily or on-demand.

---

## ✅ Summary

| Tool       | Role                          |
|------------|-------------------------------|
| FastAPI    | Ingests & writes Parquet      |
| dbt        | Transforms and aggregates     |
| DuckDB     | SQL engine used by dbt        |
| Makefile   | Easy CLI-based orchestration  |
| Airflow    | (Optional) Orchestration layer|

This setup gives you full control over ingesting, modeling, and scheduling your lakehouse pipeline locally or in production.

