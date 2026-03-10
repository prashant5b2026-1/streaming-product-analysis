-- growth analysis over the years 

SELECT
year_added,
COUNT(*) AS titles_added,
LAG(COUNT(*)) OVER (ORDER BY year_added) AS previous_year,
ROUND(
(COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year_added))::decimal
/
LAG(COUNT(*)) OVER (ORDER BY year_added) * 100,
2
) AS growth_rate
FROM netflix_content
GROUP BY year_added
ORDER BY year_added;