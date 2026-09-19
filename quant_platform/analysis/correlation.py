"""Correlation analysis: static cross-asset matrices and rolling pair correlations."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def calculate_correlation_matrix(
    returns_or_prices: pd.DataFrame,
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Calculate static correlation matrix across multiple assets.

    Parameters:
        returns_or_prices: DataFrame where columns represent asset returns or prices.
        method: 'pearson', 'spearman', or 'kendall'.

    Returns:
        Correlation matrix DataFrame.
    """
    return returns_or_prices.corr(method=method)


def calculate_rolling_correlation(
    series1: pd.Series,
    series2: pd.Series,
    window: int = 90,
) -> pd.Series:
    """
    Calculate rolling correlation between two asset series.

    Parameters:
        series1: First asset returns or prices.
        series2: Second asset returns or prices.
        window: Rolling window size (bars).

    Returns:
        Series of rolling correlation values between -1.0 and 1.0.
    """
    if window < 2:
        raise ValueError("Rolling correlation window must be >= 2.")
    return series1.rolling(window=window, min_periods=window).corr(series2)


def calculate_all_rolling_correlations(
    returns_df: pd.DataFrame,
    window: int = 90,
) -> pd.DataFrame:
    """
    Calculate rolling correlations for all unique pairs of assets in returns_df.

    Parameters:
        returns_df: DataFrame with asset daily returns as columns.
        window: Lookback window in days.

    Returns:
        DataFrame with columns named 'AssetA / AssetB'.
    """
    cols = list(returns_df.columns)
    rolling_pairs = pd.DataFrame(index=returns_df.index)

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a1, a2 = cols[i], cols[j]
            pair_name = f"{a1} vs {a2}"
            rolling_pairs[pair_name] = calculate_rolling_correlation(
                returns_df[a1],
                returns_df[a2],
                window=window,
            )

    return rolling_pairs
