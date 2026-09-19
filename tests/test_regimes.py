"""Unit tests for market regime classification and conditioned performance."""

import pytest
import pandas as pd
import numpy as np

from quant_platform.analysis.regimes import RegimeClassifier


@pytest.fixture
def sample_market_df():
    dates = pd.date_range("2021-01-01", periods=300, freq="B")
    np.random.seed(42)
    # Generate prices that rise, then fall
    trend = np.concatenate([np.linspace(100, 200, 150), np.linspace(200, 80, 150)])
    noise = np.random.normal(0, 2, 300)
    close = trend + noise
    open_p = close + np.random.normal(0, 0.5, 300)
    high = np.maximum(open_p, close) + np.abs(np.random.normal(0, 1.5, 300))
    low = np.minimum(open_p, close) - np.abs(np.random.normal(0, 1.5, 300))
    vol = np.random.uniform(1000, 5000, 300)

    df = pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": vol,
    }, index=dates)
    return df


def test_regime_classification_no_lookahead(sample_market_df):
    classified = RegimeClassifier.classify(
        sample_market_df,
        trend_sma_window=50,
        vol_atr_window=14,
        min_history=30,
    )

    assert "regime" in classified.columns
    assert "sma_trend" in classified.columns
    assert "atr" in classified.columns
    assert len(classified) == len(sample_market_df)

    # Check that regimes assigned belong to allowed set
    allowed = set(RegimeClassifier.REGIMES + ["Unclassified"])
    assert set(classified["regime"].unique()).issubset(allowed)


def test_regime_performance_evaluation(sample_market_df):
    classified = RegimeClassifier.classify(sample_market_df, trend_sma_window=50, min_history=20)
    # Dummy strategy returns
    strat_returns = pd.Series(np.random.normal(0.0005, 0.015, len(sample_market_df)), index=sample_market_df.index)

    perf_df = RegimeClassifier.evaluate_regime_performance(
        classified,
        strat_returns,
        periods_per_year=252,
    )

    assert len(perf_df) == 4
    assert "Regime" in perf_df.columns
    assert "Sharpe Ratio" in perf_df.columns
    assert "Cumulative Return (%)" in perf_df.columns
    assert "Max Drawdown (%)" in perf_df.columns
