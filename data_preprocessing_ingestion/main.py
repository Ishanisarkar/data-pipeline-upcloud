import os
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shutil
from trino.dbapi import connect

app = FastAPI()

EXPECTED_SCHEMA = {
    'timestamp': 'object',
    'resource_id': 'object',
    'user_id': 'int64',
    'credit_usage': 'float64',
    'region': 'object',
    'service_tier': 'object',
    'operation_type': 'object',
    'success': 'bool',
    'resource_type': 'object',
    'invoice_id': 'object',
    'currency': 'object'
}

class WriteRequest(BaseModel):
    bucket: str
    date: str


class SyncRequest(BaseModel):
    catalog: str = "iceberg"
    schema: str = "default"
    table: str

def validate_and_cast_schema(df):
    for col, dtype in EXPECTED_SCHEMA.items():
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
        try:
            if dtype.startswith("int") or dtype.startswith("float"):
                df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
            elif dtype == "bool":
                df[col] = df[col].astype(bool)
            else:
                df[col] = df[col].astype(str)
        except Exception as e:
            raise ValueError(f"Failed to cast column {col}: {e}")
    return df

def preprocess(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['year'] = df['timestamp'].dt.year.astype(str).str.zfill(4)
    df['month'] = df['timestamp'].dt.month.astype(str).str.zfill(2)
    df['day'] = df['timestamp'].dt.day.astype(str).str.zfill(2)
    return df

def write_parquet(df, output_base):
    partition_path = Path(output_base) / f"year={df['year'].iloc[0]}/month={df['month'].iloc[0]}/day={df['day'].iloc[0]}"
    if partition_path.exists():
        shutil.rmtree(partition_path)

    schema = pa.schema([
        ("timestamp", pa.timestamp("ns")),
        ("resource_id", pa.string()),
        ("user_id", pa.int64()),
        ("credit_usage", pa.float64()),
        ("region", pa.string()),
        ("service_tier", pa.string()),
        ("operation_type", pa.string()),
        ("success", pa.bool_()),
        ("resource_type", pa.string()),
        ("invoice_id", pa.string()),
        ("currency", pa.string()),
        ("year", pa.string()),      
        ("month", pa.string()),   
        ("day", pa.string())       
    ])

    table = pa.Table.from_pandas(df, preserve_index=False)
    ds.write_dataset(
        table,
        base_dir=output_base,
        format="parquet",
        partitioning=ds.partitioning(
            pa.schema([
                ("year", pa.string()),
                ("month", pa.string()),
                ("day", pa.string())
            ]),
            flavor="hive"
        ),
        existing_data_behavior="overwrite_or_ignore"
    )
    return str(partition_path)

@app.post("/write")
def write_partitioned_data(request: WriteRequest):
    try:
        dt = datetime.strptime(request.date, "%Y-%m-%d")
        input_path = Path(request.bucket) / f"year={dt.year}/month={dt.month:02}/day={dt.day:02}/billing.csv"
        print(input_path)
        if not input_path.exists():
            raise HTTPException(status_code=404, detail=f"Input file not found: {input_path}")

        df = pd.read_csv(input_path)
        df = validate_and_cast_schema(df)
        df = preprocess(df)

        output_path = "/datawarehouse/default/billing"
        written_path = write_parquet(df, output_path)

        return {"status": "success", "path": written_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
