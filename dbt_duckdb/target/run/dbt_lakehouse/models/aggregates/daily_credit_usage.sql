
      create or replace view "lakehouse"."main"."daily_credit_usage__dbt_int" as (
        select * from read_parquet('../datawarehouse/aggregates/daily_credit_usage/daily_credit_usage_2025-04-23.parquet', union_by_name=False)
        -- if relation is empty, filter by all columns having null values
        
      );
    