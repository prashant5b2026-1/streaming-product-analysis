-- genre growth comparison (latest year vs prior year)

WITH yearly_genre AS (
  SELECT
    year_added,
    primary_genre,
    COUNT(*) AS titles
  FROM netflix_content
  WHERE year_added IS NOT NULL
  GROUP BY year_added, primary_genre
),
latest AS (
  SELECT MAX(year_added) AS year FROM yearly_genre
),
this_year AS (
  SELECT year_added, primary_genre, titles
  FROM yearly_genre
  WHERE year_added = (SELECT year FROM latest)
),
prior_year AS (
  SELECT year_added, primary_genre, titles
  FROM yearly_genre
  WHERE year_added = (SELECT year FROM latest) - 1
)
SELECT
  t.primary_genre,
  t.titles AS current_titles,
  p.titles AS prior_titles,
  ROUND(
    (t.titles - COALESCE(p.titles, 0))::decimal
      / NULLIF(GREATEST(p.titles, 1), 0) * 100,
    1
  ) AS growth_pct
FROM this_year t
LEFT JOIN prior_year p ON t.primary_genre = p.primary_genre
ORDER BY growth_pct DESC NULLS LAST
LIMIT 20;
