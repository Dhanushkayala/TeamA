"""Moving average indicators (SMA, EMA) with vectorized computation."""

import pandas as pd
import numpy as np
from typing import Union


def calculate_sma(series: Union[pd.Series, pd.DataFrame], window: int) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate Simple Moving Average (SMA) over a given window.

    Parameters:
        series: Price series (e.g., Close price) or DataFrame of prices.
        window: Integer rolling window size (must be >= 1).

    Returns:
        SMA series or DataFrame of same shape.
    """
    if window < 1:
        raise ValueError("Window size must be at least 1.")
    return series.rolling(window=window, min_periods=window).mean()


def calculate_ema(series: Union[pd.Series, pd.DataFrame], span: int) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate Exponential Moving Average (EMA) over a given span.

    Parameters:
        series: Price series or DataFrame.
        span: Decay span for EMA (alpha = 2 / (span + 1), must be >= 1).

    Returns:
        EMA series or DataFrame of same shape.
    """
    if span < 1:
        raise ValueError("Span must be at least 1.")
    return series.ewm(span=span, adjust=False, min_periods=span).mean()
