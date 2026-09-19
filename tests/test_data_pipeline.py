"""Unit tests for multi-asset data fetching, cleaning, caching, and calendar alignment."""

import pytest
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

from quant_platform.data.cleaner import DataCleaner, DataValidationError
from quant_platform.data.cache import DiskCache
from quant_platform.data.fetcher import DataFetcher
from quant_platform.data.aligner import MultiAssetAligner


def test_cleaner_validation_and_deduplication():
    # Build dataframe with duplicate dates, inverted high/low, negative values
    dates = pd.to_datetime(["2023-01-01", "2023-01-01", "2023-01-02", "2023-01-03"])
    df = pd.DataFrame({
        "Open": [100.0, 101.0, 102.0, -5.0],
        "High": [105.0, 106.0, 101.0, 110.0],  # Day 3 has High(101) < Low(103)
        "Low": [95.0, 96.0, 103.0, 90.0],
        "Close": [102.0, 103.0, 102.5, 105.0],
        "Volume": [1000, 1200, 1500, 1100],
    }, index=dates)

    clean_df, stats = DataCleaner.validate_and_clean(df, asset_name="TestAsset")

    assert len(clean_df) == 3
    assert stats["duplicate_dates_dropped"] == 1
    assert stats["high_low_violations"] == 1
    assert stats["negative_prices_detected"] == 1
    assert clean_df.index.is_monotonic_increasing
    assert not clean_df.index.has_duplicates
    assert (clean_df["high"] >= clean_df["low"]).all()
    assert (clean_df["open"] > 0).all()


def test_cleaner_empty_raises():
    with pytest.raises(DataValidationError):
        DataCleaner.validate_and_clean(pd.DataFrame())


def test_cache_roundtrip(tmp_path):
    cache = DiskCache(cache_dir=tmp_path)
    dates = pd.date_range("2023-01-01", "2023-01-10", freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 110, len(dates))}, index=dates)
    
    assert cache.get("TEST_SYM") is None
    cache.put("TEST_SYM", df)
    
    retrieved = cache.get("TEST_SYM", start_date="2023-01-02", end_date="2023-01-08")
    assert retrieved is not None
    assert len(retrieved) == 7
    assert retrieved.index[0] == pd.to_datetime("2023-01-02")
    assert retrieved.index[-1] == pd.to_datetime("2023-01-08")


def test_data_fetcher_synthetic_generation():
    fetcher = DataFetcher(use_cache=False)
    df, info = fetcher.fetch_asset("Bitcoin", start_date="2022-01-01", end_date="2022-06-01")
    assert not df.empty
    assert "close" in df.columns
    assert "open" in df.columns
    assert (df["close"] > 0).all()
    assert df.index.min() >= pd.to_datetime("2022-01-01")


def test_multi_asset_alignment_no_backfill():
    """
    Critical requirement test:
    - Bitcoin trades weekends (e.g. Sat/Sun 2023-01-07, 2023-01-08)
    - Gold/NVDA trade weekdays only
    - Forward-fill only; no backfill leaks future data
    """
    btc_dates = pd.date_range("2023-01-02", "2023-01-08", freq="D")  # Mon to Sun
    equity_dates = pd.date_range("2023-01-02", "2023-01-06", freq="B")  # Mon to Fri

    btc_df = pd.DataFrame({"close": [10, 11, 12, 13, 14, 15, 16]}, index=btc_dates)
    nvda_df = pd.DataFrame({"close": [100, 102, 101, 104, 106]}, index=equity_dates)

    # Add a mid-week missing bar in Gold (e.g. holiday on Wed Jan 4)
    gold_dates = pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-05", "2023-01-06"])
    gold_df = pd.DataFrame({"close": [1800.0, 1810.0, 1820.0, 1830.0]}, index=gold_dates)

    asset_dfs = {"Bitcoin": btc_df, "NVIDIA": nvda_df, "Gold": gold_df}
    aligned_dfs, aligned_close, fill_stats = MultiAssetAligner.align(asset_dfs, calendar_mode="equity")

    assert len(aligned_close) == 5  # Mon-Fri
    assert "Bitcoin" in aligned_close.columns
    assert "NVIDIA" in aligned_close.columns
    assert "Gold" in aligned_close.columns

    # Gold had 1 missing day (Jan 4), which must be forward-filled with Jan 3 value (1810.0), NOT Jan 5 (1820.0)
    jan4 = pd.to_datetime("2023-01-04")
    assert aligned_close.loc[jan4, "Gold"] == 1810.0
    assert fill_stats["Gold"] == 1
    assert fill_stats["NVIDIA"] == 0
