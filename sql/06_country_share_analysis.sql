-- country share analysis

SELECT
primary_country,
COUNT(*) AS titles,
ROUND(
COUNT(*) * 100.0 /
SUM(COUNT(*)) OVER(),
2
) AS catalog_share
FROM netflix_content
GROUP BY primary_country
ORDER BY titles DESC
LIMIT 10;