-- pareto analysis on primary genre

SELECT
primary_genre,
COUNT(*) AS titles,
SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) AS cumulative_titles
FROM netflix_content
GROUP BY primary_genre
ORDER BY titles DESC;