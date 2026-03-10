-- top genres by year analysis

SELECT *
FROM (
SELECT
year_added,
primary_genre,
COUNT(*) AS titles,
RANK() OVER(
PARTITION BY year_added
ORDER BY COUNT(*) DESC
) AS genre_rank
FROM netflix_content
GROUP BY year_added, primary_genre
) ranked
WHERE genre_rank <= 3;