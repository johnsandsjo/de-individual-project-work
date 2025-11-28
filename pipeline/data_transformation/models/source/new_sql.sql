-- staging model for scb_stats

WITH source AS (
    SELECT * FROM {{ source('dbt_agent', 'scb_stats') }}
),

renamed AS (
    SELECT
        universitet_h_gskola AS university,
        examen AS exam,
        utbildningsl_ngd AS education_length,
        k_n AS gender,
        _2023_24 AS num_students,
        _dlt_load_id AS dlt_load_id,
        _dlt_id AS dlt_id
    FROM source
)

SELECT * FROM renamed