"""Oscillators, ATR, and statistical indicators."""

import pandas as pd
import numpy as np
from typing import Tuple, Union


def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR) based on High, Low, and Close prices.

    True Range = max(High - Low, abs(High - Close_prev), abs(Low - Close_prev))
    """
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=window, min_periods=window).mean()
    return atr


def calculate_bollinger_bands(
    series: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands: (Middle Band / SMA, Upper Band, Lower Band).
    """
    middle = series.rolling(window=window, min_periods=window).mean()
    std = series.rolling(window=window, min_periods=window).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    return middle, upper, lower


def calculate_zscore(series: pd.Series, window: int = 30) -> pd.Series:
    """
    Calculate rolling Z-score: (Price - Rolling_Mean) / Rolling_Std.
    """
    rolling_mean = series.rolling(window=window, min_periods=window).mean()
    rolling_std = series.rolling(window=window, min_periods=window).std()
    zscore = (series - rolling_mean) / rolling_std.replace(0.0, np.nan)
    return zscore.replace([np.inf, -np.inf], np.nan)

