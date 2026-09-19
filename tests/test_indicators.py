"""Unit tests for quantitative indicators and correlation engine."""

import pytest
import pandas as pd
import numpy as np

from quant_platform.indicators.moving_averages import calculate_sma, calculate_ema
from quant_platform.indicators.returns import (
    calculate_daily_returns,
    calculate_log_returns,
    calculate_cumulative_returns,
    calculate_rolling_returns,
)
from quant_platform.indicators.risk_metrics import (
    calculate_volatility,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_drawdown_series,
    calculate_max_drawdown,
    calculate_cagr,
)
from quant_platform.indicators.oscillators import (
    calculate_atr,
    calculate_bollinger_bands,
    calculate_zscore,
)
from quant_platform.analysis.correlation import (
    calculate_correlation_matrix,
    calculate_rolling_correlation,
    calculate_all_rolling_correlations,
)


@pytest.fixture
def sample_price_series():
    dates = pd.date_range("2023-01-01", periods=100, freq="B")
    np.random.seed(42)
    # Drift of 0.05, daily noise
    returns = np.random.normal(0.001, 0.02, size=100)
    prices = 100.0 * np.cumprod(1 + returns)
    return pd.Series(prices, index=dates, name="Price")


def test_sma_ema(sample_price_series):
    sma20 = calculate_sma(sample_price_series, window=20)
    ema20 = calculate_ema(sample_price_series, span=20)

    assert len(sma20) == len(sample_price_series)
    assert sma20.iloc[18] is np.nan or pd.isna(sma20.iloc[18])
    assert not pd.isna(sma20.iloc[19])
    assert not pd.isna(ema20.iloc[19])
    # Mathematical validation for simple series
    s = pd.Series([10.0, 20.0, 30.0, 40.0])
    assert calculate_sma(s, 2).iloc[1] == 15.0


def test_returns(sample_price_series):
    daily = calculate_daily_returns(sample_price_series)
    cum = calculate_cumulative_returns(daily)
    log_r = calculate_log_returns(sample_price_series)

    assert pd.isna(daily.iloc[0])
    assert cum.iloc[0] == 0.0
    assert np.isclose(cum.iloc[-1], (sample_price_series.iloc[-1] / sample_price_series.iloc[0]) - 1.0)
    assert np.isclose(np.exp(log_r.dropna().sum()), (sample_price_series.iloc[-1] / sample_price_series.iloc[0]))


def test_sharpe_and_drawdown():
    # Deterministic test series: constant 1% return daily with no risk-free rate
    dates = pd.date_range("2023-01-01", periods=50, freq="B")
    # Alternating returns +2% and 0% -> mean 1%, std > 0
    rets = pd.Series([0.02, 0.00] * 25, index=dates)
    
    ann_vol = calculate_annualized_volatility(rets, periods_per_year=252)
    assert ann_vol > 0
    
    sharpe = calculate_sharpe_ratio(rets, risk_free_rate=0.0, periods_per_year=252)
    assert sharpe > 0

    # Drawdown test: Price goes 100 -> 120 -> 90 -> 110
    p = pd.Series([100.0, 120.0, 90.0, 110.0])
    dds = calculate_drawdown_series(p)
    # Peak at 120, trough at 90 -> drawdown = (90-120)/120 = -0.25 (-25%)
    assert dds.iloc[0] == 0.0
    assert dds.iloc[1] == 0.0
    assert np.isclose(dds.iloc[2], -0.25)
    assert calculate_max_drawdown(p) == -0.25


def test_cagr():
    # 100 to 200 in 252 business days (1 year) -> CAGR = 100%
    dates = pd.date_range("2023-01-01", periods=252, freq="B")
    p = pd.Series(np.linspace(100, 200, 252), index=dates)
    cagr = calculate_cagr(p, periods_per_year=252)
    assert np.isclose(cagr, 1.0, atol=0.01)


def test_correlation_matrix_and_rolling():
    dates = pd.date_range("2023-01-01", periods=100, freq="B")
    np.random.seed(42)
    a = np.random.normal(0, 1, 100)
    b = a * 0.8 + np.random.normal(0, 0.6, 100)
    c = -a * 0.5 + np.random.normal(0, 0.8, 100)

    df = pd.DataFrame({"AssetA": a, "AssetB": b, "AssetC": c}, index=dates)
    
    corr_mat = calculate_correlation_matrix(df)
    assert corr_mat.shape == (3, 3)
    assert np.isclose(corr_mat.loc["AssetA", "AssetA"], 1.0)
    assert corr_mat.loc["AssetA", "AssetB"] > 0.5
    assert corr_mat.loc["AssetA", "AssetC"] < 0.0

    rolling_pairs = calculate_all_rolling_correlations(df, window=30)
    assert "AssetA vs AssetB" in rolling_pairs.columns
    assert len(rolling_pairs) == 100
    assert not pd.isna(rolling_pairs["AssetA vs AssetB"].iloc[40])
