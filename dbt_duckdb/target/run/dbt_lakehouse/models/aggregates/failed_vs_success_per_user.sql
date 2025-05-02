
      create or replace view "lakehouse"."main"."failed_vs_success_per_user__dbt_int" as (
        select * from read_parquet('../datawarehouse/aggregates/failed_vs_success_per_user/failed_vs_success_per_user2025-04-23.parquet', union_by_name=False)
        -- if relation is empty, filter by all columns having null values
        
      );
    