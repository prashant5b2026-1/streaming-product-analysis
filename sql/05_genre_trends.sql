-- genre trend analysis 

SELECT
year_added,
primary_genre,
COUNT(*) AS titles_added
FROM netflix_content
GROUP BY year_added, primary_genre
ORDER BY year_added;