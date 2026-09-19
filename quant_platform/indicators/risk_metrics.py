"""Risk and performance metrics (Sharpe ratio, Sortino ratio, Volatility, Drawdown, CAGR, Calmar)."""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Optional


def calculate_volatility(returns: Union[pd.Series, pd.DataFrame], window: Optional[int] = None) -> Union[float, pd.Series, pd.DataFrame]:
    """
    Calculate sample standard deviation of returns.
    
    Parameters:
        returns: Daily returns series or DataFrame.
        window: If specified, computes rolling standard deviation. Otherwise, full-period sample std.
    """
    if window is not None:
        return returns.rolling(window=window, min_periods=window).std()
    return returns.std()


def calculate_annualized_volatility(
    returns: Union[pd.Series, pd.DataFrame],
    periods_per_year: int = 252,
    window: Optional[int] = None,
) -> Union[float, pd.Series, pd.DataFrame]:
    """
    Calculate annualized volatility: std * sqrt(periods_per_year).

    Convention:
        - Equities & Commodities (Gold): periods_per_year = 252
        - Crypto (Bitcoin 24/7): periods_per_year = 365
    """
    vol = calculate_volatility(returns, window=window)
    return vol * np.sqrt(periods_per_year)


def calculate_sharpe_ratio(
    returns: Union[pd.Series, pd.DataFrame],
    risk_free_rate: float = 0.04,
    periods_per_year: int = 252,
    window: Optional[int] = None,
) -> Union[float, pd.Series, pd.DataFrame]:
    """
    Calculate annualized Sharpe Ratio:
        Sharpe = (mean(r - r_f) / std(r - r_f)) * sqrt(periods_per_year)

    Parameters:
        returns: Daily return series or DataFrame.
        risk_free_rate: Annualized risk-free rate (e.g. 0.04 for 4%).
        periods_per_year: 252 for equities/gold, 365 for crypto.
        window: If set, computes rolling annualized Sharpe ratio.
    """
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_returns = returns - daily_rf

    if window is not None:
        rolling_mean = excess_returns.rolling(window=window, min_periods=window).mean()
        rolling_std = excess_returns.rolling(window=window, min_periods=window).std()
        # Avoid division by zero
        rolling_sharpe = (rolling_mean / rolling_std.replace(0.0, np.nan)) * np.sqrt(periods_per_year)
        return rolling_sharpe.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    mean_excess = excess_returns.mean()
    std_excess = excess_returns.std()

    if isinstance(std_excess, pd.Series):
        sharpe = (mean_excess / std_excess.replace(0.0, np.nan)) * np.sqrt(periods_per_year)
        return sharpe.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    if std_excess == 0 or np.isnan(std_excess):
        return 0.0
    return float((mean_excess / std_excess) * np.sqrt(periods_per_year))


def calculate_downside_deviation(
    returns: Union[pd.Series, pd.DataFrame],
    risk_free_rate: float = 0.04,
    periods_per_year: int = 252,
) -> Union[float, pd.Series]:
    """
    Calculate annualized downside semi-deviation (bad volatility):
        Downside Deviation = sqrt( mean( min(r - r_f, 0)^2 ) ) * sqrt(periods_per_year)
    """
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_returns = returns - daily_rf
    downside = np.minimum(excess_returns, 0.0)
    
    if isinstance(returns, pd.DataFrame):
        sq_mean = (downside ** 2).mean()
        return np.sqrt(sq_mean) * np.sqrt(periods_per_year)
    
    clean_downside = downside.dropna()
    if len(clean_downside) == 0:
        return 0.0
    sq_mean = float((clean_downside ** 2).mean())
    return float(np.sqrt(sq_mean) * np.sqrt(periods_per_year))


def calculate_sortino_ratio(
    returns: Union[pd.Series, pd.DataFrame],
    risk_free_rate: float = 0.04,
    periods_per_year: int = 252,
) -> Union[float, pd.Series]:
    """
    Calculate annualized Sortino Ratio:
        Sortino = (mean(r - r_f) * periods_per_year) / annualized_downside_deviation
    """
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_returns = returns - daily_rf
    
    ann_mean_excess = excess_returns.mean() * periods_per_year
    ann_downside_dev = calculate_downside_deviation(returns, risk_free_rate=risk_free_rate, periods_per_year=periods_per_year)
    
    if isinstance(returns, pd.DataFrame):
        sortino = ann_mean_excess / ann_downside_dev.replace(0.0, np.nan)
        return sortino.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    
    if ann_downside_dev == 0 or np.isnan(ann_downside_dev):
        return 0.0 if ann_mean_excess <= 0 else float("inf")
    
    return float(ann_mean_excess / ann_downside_dev)


def calculate_drawdown_series(prices_or_equity: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate underwater drawdown series: DD_t = (Value_t / CumMax_t) - 1.0.
    
    Returns series of non-positive numbers (e.g., -0.15 for a 15% drawdown).
    """
    cummax = prices_or_equity.cummax()
    drawdown = (prices_or_equity / cummax) - 1.0
    return drawdown


def calculate_max_drawdown(prices_or_equity: Union[pd.Series, pd.DataFrame]) -> Union[float, pd.Series]:
    """
    Calculate Maximum Drawdown (MDD) as a negative float (or Series for DataFrame).
    Example: -0.25 represents a 25% peak-to-trough decline.
    """
    dd = calculate_drawdown_series(prices_or_equity)
    res = dd.min()
    if isinstance(res, (float, int, np.floating)):
        return 0.0 if np.isnan(res) else float(res)
    return res


def calculate_cagr(
    equity_or_prices: Union[pd.Series, pd.DataFrame],
    periods_per_year: int = 252,
) -> Union[float, pd.Series]:
    """
    Calculate Compound Annual Growth Rate (CAGR):
        CAGR = (Ending Value / Beginning Value) ** (periods_per_year / total_periods) - 1
    """
    clean_series = equity_or_prices.dropna()
    total_periods = len(clean_series)
    if total_periods < 2:
        return 0.0

    if isinstance(clean_series, pd.DataFrame):
        start_val = clean_series.iloc[0]
        end_val = clean_series.iloc[-1]
        cagr = (end_val / start_val) ** (periods_per_year / total_periods) - 1.0
        return cagr

    start_val = float(clean_series.iloc[0])
    end_val = float(clean_series.iloc[-1])
    if start_val <= 0 or end_val <= 0:
        return 0.0
    
    return float((end_val / start_val) ** (periods_per_year / total_periods) - 1.0)


def calculate_calmar_ratio(cagr: float, max_drawdown: float) -> float:
    """
    Calculate Calmar Ratio: CAGR / abs(Max Drawdown).
    """
    if max_drawdown >= 0 or np.isnan(max_drawdown) or max_drawdown == 0:
        return 0.0
    return float(cagr / abs(max_drawdown))

