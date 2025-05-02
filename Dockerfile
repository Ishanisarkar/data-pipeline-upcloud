FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y curl unzip

# Install DuckDB CLI
RUN curl -L https://github.com/duckdb/duckdb/releases/download/v0.9.2/duckdb_cli-linux-amd64.zip -o duckdb.zip \
    && unzip duckdb.zip -d /usr/local/bin \
    && rm duckdb.zip

# Install dbt and Python bindings
RUN pip install dbt-duckdb duckdb

# Set working directory
WORKDIR /app

COPY dbt_duckdb/ /app
