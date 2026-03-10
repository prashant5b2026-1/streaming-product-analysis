-- genre market share analysis

SELECT
primary_genre,
COUNT(*) AS titles,
ROUND(
COUNT(*) * 100.0 /
SUM(COUNT(*)) OVER(),
2
) AS catalog_share
FROM netflix_content
GROUP BY primary_genre
ORDER BY titles DESC;