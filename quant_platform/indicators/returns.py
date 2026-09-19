"""Vectorized return calculation functions."""

import pandas as pd
import numpy as np
from typing import Union


def calculate_daily_returns(prices: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate simple arithmetic daily percentage returns: (P_t - P_{t-1}) / P_{t-1}.

    Parameters:
        prices: Series or DataFrame of asset prices.

    Returns:
        Series or DataFrame of daily returns with NaN for the first element.
    """
    return prices.pct_change()


def calculate_log_returns(prices: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate continuously compounded log returns: ln(P_t / P_{t-1}).

    Parameters:
        prices: Series or DataFrame of asset prices.

    Returns:
        Series or DataFrame of log returns.
    """
    return np.log(prices / prices.shift(1))


def calculate_cumulative_returns(returns: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate cumulative compounding returns from daily returns: prod(1 + r_t) - 1.

    Parameters:
        returns: Daily arithmetic returns.

    Returns:
        Cumulative returns series or DataFrame starting from 0.0.
    """
    clean_rets = returns.fillna(0.0)
    return (1.0 + clean_rets).cumprod() - 1.0


def calculate_rolling_returns(prices: Union[pd.Series, pd.DataFrame], window: int) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate rolling k-period returns: (P_t - P_{t-window}) / P_{t-window}.

    Parameters:
        prices: Series or DataFrame of asset prices.
        window: Number of periods for lookback.

    Returns:
        Rolling returns series.
    """
    if window < 1:
        raise ValueError("Rolling return window must be >= 1.")
    return prices.pct_change(periods=window)
