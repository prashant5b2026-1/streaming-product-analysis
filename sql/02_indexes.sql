CREATE INDEX idx_year_added
ON netflix_content(year_added);

CREATE INDEX idx_primary_genre
ON netflix_content(primary_genre);

CREATE INDEX idx_type 
ON netflix_content(type);

CREATE INDEX idx_primary_country
ON netflix_content(primary_country);
