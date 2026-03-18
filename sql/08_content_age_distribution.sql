-- content age distribution

SELECT
  content_age AS age,
  COUNT(*) AS titles,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_catalog
FROM netflix_content
WHERE content_age IS NOT NULL
GROUP BY content_age
ORDER BY content_age;
