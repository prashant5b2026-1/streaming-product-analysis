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

-- fastest growing genre over the last 5 years 

WITH yearly_genre AS (
    SELECT year_added, primary_genre, COUNT(*) AS titles
    FROM netflix_content 
    GROUP BY year_added, primary_genre 
)
SELECT year_added, primary_genre, titles
FROM yearly_genre 
WHERE year_added >= (SELECT MAX(year_added) - 4 FROM netflix_content)
ORDER BY year_added DESC, titles DESC;
