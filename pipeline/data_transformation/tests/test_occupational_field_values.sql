SELECT
    occupation_field
FROM {{ ref('dim_occupation') }}
WHERE occupation_field NOT IN ('Data/IT', 'Yrken med teknisk inriktning')