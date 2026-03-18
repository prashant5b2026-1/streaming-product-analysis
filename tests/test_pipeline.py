"""Unit tests for key pipeline functions."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.feature_engineering import feature_engineer
from etl.data_quality import data_quality_report


class TestFeatureEngineering:
    """Test the feature engineering module."""

    def test_feature_engineer_basic(self):
        """Test that feature_engineer adds expected columns."""
        # Create sample data
        sample_data = {
            'show_id': ['s1', 's2'],
            'type': ['Movie', 'TV Show'],
            'title': ['Movie 1', 'Show 1'],
            'director': ['Director A', ''],
            'cast': ['Actor A, Actor B', ''],
            'country': ['United States', 'India'],
            'date_added': ['January 1, 2020', 'February 1, 2020'],
            'release_year': [2020, 2019],
            'rating': ['TV-MA', 'TV-14'],
            'duration': ['90 min', '1 Season'],
            'listed_in': ['Action, Drama', 'Comedy'],
            'description': ['A great movie', 'A fun show']
        }
        df = pd.DataFrame(sample_data)

        # Run feature engineering
        result = feature_engineer(df)

        # Check that new columns were added
        expected_columns = [
            'genre_list', 'main_genre', 'country_list', 'main_country',
            'is_movie', 'is_tv_show', 'duration_minutes', 'seasons_count',
            'date_added_parsed', 'days_since_added'
        ]

        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"

        # Check data types
        assert result['is_movie'].dtype == bool
        assert result['is_tv_show'].dtype == bool
        assert result['duration_minutes'].dtype == 'Int64'
        assert result['seasons_count'].dtype == 'Int64'

    def test_feature_engineer_empty_data(self):
        """Test feature_engineer handles empty dataframes."""
        df = pd.DataFrame()
        result = feature_engineer(df)
        assert len(result) == 0


class TestDataQuality:
    """Test the data quality module."""

    def test_data_quality_report_basic(self):
        """Test that data_quality_report generates expected metrics."""
        # Create sample data
        sample_data = {
            'show_id': ['s1', 's2', 's3'],
            'type': ['Movie', 'TV Show', 'Movie'],
            'title': ['Movie 1', 'Show 1', 'Movie 2'],
            'release_year': [2020, 2019, 2021],
            'rating': ['TV-MA', 'TV-14', 'PG-13'],
            'duration_minutes': [90, None, 120],
            'is_movie': [True, False, True]
        }
        df = pd.DataFrame(sample_data)

        # Generate report
        report = data_quality_report(df)

        # Check that report has expected structure
        assert 'total_rows' in report
        assert 'total_columns' in report
        assert 'missing_values' in report
        assert 'duplicate_rows' in report
        assert 'data_types' in report

        # Check values
        assert report['total_rows'] == 3
        assert report['total_columns'] == len(df.columns)
        assert isinstance(report['missing_values'], dict)
        assert isinstance(report['data_types'], dict)


if __name__ == "__main__":
    pytest.main([__file__])
