"""
Unit tests for DataLoader (data loading, cleaning, filtering, and error handling).
"""
import pytest
import pandas as pd
import numpy as np
from app.data_loader import DataLoader, DataLoaderError

@pytest.fixture
def sample_price_df():
    dates = pd.date_range('2024-01-01', periods=5)
    df = pd.DataFrame({
        'AAA': np.linspace(100, 104, 5),
        'BBB': np.linspace(200, 204, 5)
    }, index=dates)
    df.index.name = 'Date'
    return df

def test_clean_sets_index_and_numeric(sample_price_df):
    dl = DataLoader(source_url=None)
    dl.data = sample_price_df.copy()
    cleaned = dl.clean()
    assert isinstance(cleaned, pd.DataFrame)
    assert 'Date' not in cleaned.columns
    assert cleaned.index.name == 'Date'
    assert cleaned.shape == (5, 2)
    assert cleaned.isnull().sum().sum() == 0
    assert cleaned.dtypes['AAA'] == float

def test_filter_dates_filters_correctly(sample_price_df):
    dl = DataLoader(source_url=None, start_date='2024-01-02', end_date='2024-01-04')
    dl.data = sample_price_df.copy()
    dl.clean()
    filtered = dl.filter_dates()
    assert filtered.index.min() >= pd.Timestamp('2024-01-02')
    assert filtered.index.max() <= pd.Timestamp('2024-01-04')
    assert filtered.shape[0] == 3

def test_get_data_raises_on_no_data():
    dl = DataLoader(source_url=None)
    with pytest.raises(DataLoaderError):
        dl.get_data()

def test_clean_warns_on_no_data(caplog):
    dl = DataLoader(source_url=None)
    with caplog.at_level('WARNING'):
        result = dl.clean()
        assert result is None
        assert "No data to clean" in caplog.text

def test_filter_dates_warns_on_no_data(caplog):
    dl = DataLoader(source_url=None)
    with caplog.at_level('WARNING'):
        result = dl.filter_dates()
        assert result is None
        assert "No data to filter" in caplog.text
