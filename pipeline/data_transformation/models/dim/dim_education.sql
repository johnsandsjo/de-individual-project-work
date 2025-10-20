WITH dim_education AS (SELECT * FROM {{ ref('src_education_stats') }})

SELECT
    {{ dbt_utils.generate_surrogate_key(['university', 'degree']) }} as education_key,
    university,
    degree,
    education_length,
    gender,
    year_2023_2024
FROM
    dim_education