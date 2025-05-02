# FastAPI-based Data Ingestion Service

This is a FastAPI application that reads billing data in CSV from a Hive-style directory structure, validates and preprocesses it, and writes Iceberg-compatible Parquet output.

---

## Inputs

POST request to `/write` with a JSON payload:

```json
{
  "bucket": "/raw_input/warehouse",
  "date": "2025-05-01"
}
```

| Field  | Type   | Description                             |
|--------|--------|-----------------------------------------|
| bucket | string | Path to root input data (mounted volume)|
| date   | string | Date partition to process (YYYY-MM-DD)  |

---

## Output

On success:
```json
{
  "status": "success",
  "path": "/warehouse/default/billing/year=2025/month=05/day=01"
}
```

On failure (e.g., file not found, empty partition):
```json
{
  "detail": "CSV loaded but contains no rows for date 2025-05-01"
}
```

---

## How to Run (Locally via Docker)

1. Make sure your directory structure looks like:

```
.
├── raw_input/
│   └── warehouse/year=2025/month=05/day=01/billing.csv
├── datawarehouse/
├── main.py
├── Dockerfile
├── requirements.txt
```

2. Build the Docker image:

```bash
docker build -t billing-api .
```

3. Run the container:

```bash
docker run --rm `
  -v "${PWD}\datawarehouse:/datawarehouse" `
  -v "${PWD}\raw_input\warehouse:/raw_input/datawarehouse" `
  -p 8000:8000 `
  billing-api
```

4. Test the API:

```bash
curl -X POST http://localhost:8000/write ^
  -H "Content-Type: application/json" ^
  -d "{"bucket": "/raw_input/warehouse", "date": "2025-05-01"}"
```

Or visit: http://localhost:8000/docs for Swagger UI.

---

## 🚀 How to Wrap as a Lambda Function

To deploy this as an AWS Lambda:

1. Replace FastAPI with a function like:
   ```python
   def lambda_handler(event, context):
       bucket = event["bucket"]
       date = event["date"]
       # Run same logic: load → validate → write
       return {"status": "success"}
   ```

2. Package dependencies using a `requirements.txt` and deploy with:
   - AWS Lambda layer
   - Docker Lambda image
   - Serverless Framework or SAM

---

## 📡 How to Invoke via Airflow

You can invoke the FastAPI service using an `HttpOperator` or `PythonOperator`:

### Option 1: Using `HttpOperator`

```python
from airflow.providers.http.operators.http import SimpleHttpOperator

write_task = SimpleHttpOperator(
    task_id="trigger_writer_api",
    method="POST",
    endpoint="/write",
    http_conn_id="billing_api",  # Defined in Airflow Connections
    headers={"Content-Type": "application/json"},
    data=json.dumps({"bucket": "/raw_input/warehouse", "date": "2025-05-01"}),
)
```

### Option 2: Use `requests` in a `PythonOperator`

```python
def trigger_writer():
    import requests
    response = requests.post(
        "http://billing-api-host:8000/write",
        json={"bucket": "/raw_input/warehouse", "date": "2025-05-01"}
    )
    response.raise_for_status()

PythonOperator(
    task_id="writer_api_call",
    python_callable=trigger_writer,
)
```

---

## Extensibility

- Add a `/sync` endpoint to trigger Trino metadata sync
- Add logging to file or database
- Add retry logic and deduplication
- Add authorization for production use

---

## Technologies

- FastAPI
- PyArrow + Pandas
- Docker
- Uvicorn
- Hive-style partitioning
- Iceberg-compatible layout
