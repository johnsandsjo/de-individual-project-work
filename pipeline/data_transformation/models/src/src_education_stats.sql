WITH source AS (
    SELECT * FROM {{ source('dbt_agent', 'scb_stats') }}
)
SELECT
    "universitet/högskola" AS university,
    examen AS degree,
    utbildningslängd AS education_length,
    kön AS gender,
    "2023/2024" AS year_2023_2024
FROM
    source