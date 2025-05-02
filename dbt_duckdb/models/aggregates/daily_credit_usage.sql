{{ config(
    materialized='external',
    location='../datawarehouse/aggregates/daily_credit_usage/daily_credit_usage_{{ var("target_date") }}.parquet',
    format='parquet',
    overwrite=True
) }}

{% set target_date = var("target_date") %}

WITH rates AS (
    SELECT * FROM (VALUES
        ('USD', 0.93),
        ('EUR', 1.0),
        ('GBP', 1.12),
        ('JPY', 0.0062)
    ) AS t(currency, rate_to_eur)
),

base AS (
    SELECT
        DATE_TRUNC('day', b.timestamp) AS date,
        b.user_id,
        b.region,
        b.currency,
        SUM(b.credit_usage) AS total_credit_usage,
        r.rate_to_eur,
        SUM(b.credit_usage) * r.rate_to_eur AS credit_usage_eur
    FROM billing b
    LEFT JOIN rates r ON b.currency = r.currency
    WHERE DATE_TRUNC('day', b.timestamp) = DATE '{{ target_date }}'
    GROUP BY 1, 2, 3, 4, 6
)

SELECT * FROM base
