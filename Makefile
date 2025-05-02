.PHONY: bootstrap run run_model run_model_date prepare_output

# Run bootstrap.sql to create billing table from partitioned Parquet
bootstrap:
	docker-compose run --rm dbt sh -c "duckdb duckdb/lakehouse.duckdb < /app/bootstrap.sql"

# Run all dbt models
run:
	docker-compose run --rm dbt dbt run

# Run specific dbt model by name
run_model:
	docker-compose run --rm dbt dbt run --select $(model)

# Prepare partition folder before writing external model
prepare_output:
	mkdir -p datawarehouse/aggregates/$(model)/date=$(target_date)

# Run specific dbt model with date var and output folder preparation
run_model_date: prepare_output
	docker-compose run --rm dbt dbt run --select $(model) --vars '{"target_date": "$(target_date)"}'
