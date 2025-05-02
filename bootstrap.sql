-- bootstrap.sql

SELECT 'running bootstrap';

CREATE OR REPLACE TABLE billing AS
SELECT *
FROM read_parquet('/datawarehouse/default/billing/year=*/month=*/day=*/*.parquet', hive_partitioning=true);
