
WITH src_occupation AS (SELECT * FROM {{ source('dbt_agent', 'stg_job_ads_bulk') }}),
src_stream_occupation AS (SELECT * FROM {{ source('dbt_agent', 'stg_job_ads_daily') }})

SELECT
    id,
    OCCUPATION__LABEL AS occupation,
    OCCUPATION_FIELD__LABEL AS occupation_field,
    OCCUPATION_GROUP__LABEL AS occupation_group,
    removed
FROM 
    src_occupation
WHERE id NOT IN (
    SELECT id
        FROM src_stream_occupation
        WHERE removed = TRUE)
UNION DISTINCT
SELECT
    id,
    OCCUPATION__LABEL AS occupation,
    OCCUPATION_FIELD__LABEL AS occupation_field,
    OCCUPATION_GROUP__LABEL AS occupation_group,
    removed
FROM 
    src_stream_occupation
WHERE removed = FALSE
