# README_first

This project is structured around two tiers of architectural documentation:

---

## `Data-Pipeline_-Architectural-Flow-Prod.pdf`

This document outlines our **ideal production architecture**, including:
- Full lakehouse integration with Iceberg, Trino, Airflow
- Monitoring, lineage, schema validation, idempotency
- Event-driven vs batch orchestration
- Best practices for scalable data pipelines

This is what we aim to implement in a real production environment.

---

## `README_architecture.md`

This markdown file documents the **actual implementation** completed during the 3-hour time-boxed technical challenge.

It includes:
- FastAPI ingestion with PyArrow
- dbt + DuckDB modeling with external Parquet materializations
- Simplified local folder-based lakehouse setup
- Reasoning behind using DuckDB for ease and speed

---

This repo reflects the foundational version of what we envision scaling into the full production system described in the PDF.

