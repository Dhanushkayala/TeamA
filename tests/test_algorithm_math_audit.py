"""Comprehensive mathematical and algorithmic correctness verification test suite."""

import pytest
import numpy as np
import pandas as pd

from quant_platform.indicators.returns import (
    calculate_daily_returns,
    calculate_log_returns,
    calculate_cumulative_returns,
    calculate_rolling_returns,
)
from quant_platform.indicators.moving_averages import calculate_sma, calculate_ema
from quant_platform.indicators.oscillators import calculate_atr, calculate_bollinger_bands, calculate_zscore
from quant_platform.indicators.risk_metrics import (
    calculate_volatility,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_downside_deviation,
    calculate_sortino_ratio,
    calculate_drawdown_series,
    calculate_max_drawdown,
    calculate_cagr,
    calculate_calmar_ratio,
)
from quant_platform.analysis.correlation import calculate_correlation_matrix, calculate_rolling_correlation
from quant_platform.analysis.regimes import RegimeClassifier
from quant_platform.backtest.strategies import (
    SMACrossoverStrategy,
    EMATrendStrategy,
    MomentumStrategy,
    MeanReversionStrategy,
)
from quant_platform.backtest.engine import BacktestEngine
from quant_platform.backtest.robustness import (
    run_parameter_sweep_ma,
    run_cost_sensitivity,
    run_train_test_split,
)
from quant_platform.data.aligner import MultiAssetAligner


# ============================================================================
# 1. RETURNS & COMPOUNDING INVARIANTS
# ============================================================================

def test_daily_returns_math():
    prices = pd.Series([100.0, 110.0, 99.0, 108.9])
    daily_rets = calculate_daily_returns(prices)
    
    assert np.isnan(daily_rets.iloc[0])
    assert pytest.approx(daily_rets.iloc[1], 1e-6) == 0.10      # (110 - 100) / 100
    assert pytest.approx(daily_rets.iloc[2], 1e-6) == -0.10     # (99 - 110) / 110
    assert pytest.approx(daily_rets.iloc[3], 1e-6) == 0.10      # (108.9 - 99) / 99


def test_cumulative_returns_compounding():
    daily_rets = pd.Series([0.10, -0.10, 0.10])
    cum_rets = calculate_cumulative_returns(daily_rets)
    
    # 1.10 * 0.90 * 1.10 = 1.089 -> +8.9%
    assert pytest.approx(cum_rets.iloc[-1], 1e-6) == 0.089


def test_log_returns_additivity():
    prices = pd.Series([100.0, 120.0, 90.0, 150.0])
    log_rets = calculate_log_returns(prices).dropna()
    
    # Sum of log returns must equal ln(P_end / P_start)
    expected_total_log_return = np.log(150.0 / 100.0)
    assert pytest.approx(log_rets.sum(), 1e-6) == expected_total_log_return


# ============================================================================
# 2. RISK METRICS MATHEMATICAL PRECISION
# ============================================================================

def test_annualized_volatility_scaling():
    # 252 days with exact constant daily volatility
    rng = np.random.default_rng(42)
    daily_rets = pd.Series(rng.normal(0.001, 0.015, size=252))
    
    sample_std = daily_rets.std()
    ann_vol_252 = calculate_annualized_volatility(daily_rets, periods_per_year=252)
    ann_vol_365 = calculate_annualized_volatility(daily_rets, periods_per_year=365)
    
    assert pytest.approx(ann_vol_252, 1e-6) == sample_std * np.sqrt(252)
    assert pytest.approx(ann_vol_365, 1e-6) == sample_std * np.sqrt(365)


def test_sharpe_ratio_formula():
    rets = pd.Series([0.01, 0.02, -0.01, 0.03, 0.01, -0.005])
    rf = 0.04
    daily_rf = (1.0 + rf) ** (1.0 / 252) - 1.0
    excess = rets - daily_rf
    expected_sharpe = (excess.mean() / excess.std()) * np.sqrt(252)
    
    calc_sharpe = calculate_sharpe_ratio(rets, risk_free_rate=rf, periods_per_year=252)
    assert pytest.approx(calc_sharpe, 1e-5) == expected_sharpe


def test_sortino_ratio_downside_deviation():
    rets = pd.Series([0.02, 0.01, -0.01, -0.02, 0.03])
    rf = 0.0
    daily_rf = (1.0 + rf) ** (1.0 / 252) - 1.0
    downside = np.minimum(rets - daily_rf, 0.0)
    expected_downside_dev = np.sqrt((downside ** 2).mean()) * np.sqrt(252)
    expected_sortino = (rets.mean() * 252) / expected_downside_dev
    
    calc_sortino = calculate_sortino_ratio(rets, risk_free_rate=rf, periods_per_year=252)
    assert pytest.approx(calc_sortino, 1e-5) == expected_sortino


def test_calmar_ratio_formula():
    cagr = 0.20
    mdd = -0.10
    calmar = calculate_calmar_ratio(cagr, mdd)
    assert pytest.approx(calmar, 1e-6) == 2.0


def test_max_drawdown_exact_values():
    prices = pd.Series([100.0, 150.0, 120.0, 105.0, 135.0, 90.0, 160.0])
    dd_series = calculate_drawdown_series(prices)
    mdd = calculate_max_drawdown(prices)
    
    # Peaks: 100, 150, 150, 150, 150, 150, 160
    # At 90.0: (90 - 150) / 150 = -60 / 150 = -0.40 (-40%)
    assert pytest.approx(mdd, 1e-6) == -0.40
    assert pytest.approx(dd_series.min(), 1e-6) == -0.40
    assert (dd_series <= 0.0).all()


def test_cagr_formula():
    dates = pd.date_range("2020-01-01", periods=504, freq="B")
    prices = pd.Series(np.linspace(100.0, 200.0, 504), index=dates)
    
    cagr = calculate_cagr(prices, periods_per_year=252)
    assert pytest.approx(cagr, 1e-4) == (2.0 ** 0.5) - 1.0


def test_zscore_zero_std():
    flat_series = pd.Series([100.0] * 50)
    z = calculate_zscore(flat_series, window=20)
    assert z.dropna().empty or z.dropna().isna().all()


# ============================================================================
# 3. BACKTEST ENGINE & STRATEGY SIGNAL INVARIANTS
# ============================================================================

def test_momentum_strategy_percentage_threshold():
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    df = pd.DataFrame({
        "open": [100.0, 100.0, 100.0, 100.0, 100.0],
        "high": [101.0, 101.0, 101.0, 101.0, 101.0],
        "low": [99.0, 99.0, 99.0, 99.0, 99.0],
        "close": [100.0, 100.5, 101.0, 101.5, 102.0],
        "volume": [1000] * 5,
    }, index=dates)
    
    # 0.5% threshold over 1-period lookback -> Day 1 return is +0.50%, Day 2 is +0.4975%
    strat = MomentumStrategy(lookback=1, threshold_pct=0.4)
    signals = strat.generate_signals(df)
    assert signals.iloc[1] == 1.0  # +0.5% > 0.4%


def test_backtest_execution_lookahead_lag():
    """Verify that signal on day t is executed on day t+1 at close with slippage."""
    dates = pd.date_range("2023-01-01", periods=10, freq="D")
    df = pd.DataFrame({
        "open": [100.0] * 10,
        "high": [105.0] * 10,
        "low": [95.0] * 10,
        "close": [100.0, 102.0, 105.0, 108.0, 110.0, 105.0, 100.0, 95.0, 90.0, 85.0],
        "volume": [1000] * 10,
    }, index=dates)

    class TestThresholdStrategy:
        name = "Threshold"
        def generate_signals(self, d):
            return (d["close"] > 103.0).astype(float)

    engine = BacktestEngine(
        initial_capital=10000.0,
        transaction_cost_pct=0.001,
        slippage_pct=0.002,
    )
    result = engine.run(df, TestThresholdStrategy())

    # Raw signal is 1.0 at t=2 (date 2023-01-03)
    assert result.signals.iloc[2] == 1.0
    assert result.signals.iloc[1] == 0.0

    # Executable position must be 0.0 at t=2 and 1.0 at t=3!
    assert result.positions.iloc[2] == 0.0
    assert result.positions.iloc[3] == 1.0

    # Entry date of trade must be t=3 (2023-01-04), at price 108.0 * (1 + 0.002) = 108.216
    assert len(result.trades) >= 1
    first_trade = result.trades[0]
    assert first_trade.entry_date == dates[3]
    assert pytest.approx(first_trade.entry_price, 1e-3) == 108.0 * 1.002
    assert "Sortino Ratio" in result.metrics["Strategy"]


def test_transaction_cost_accounting():
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    df = pd.DataFrame({
        "open": [100.0] * 5,
        "high": [100.0] * 5,
        "low": [100.0] * 5,
        "close": [100.0, 100.0, 100.0, 100.0, 100.0],
        "volume": [1000] * 5,
    }, index=dates)

    class AlwaysBuyStrategy:
        name = "Buy"
        def generate_signals(self, d):
            return pd.Series([1.0, 1.0, 1.0, 1.0, 1.0], index=d.index)

    engine = BacktestEngine(
        initial_capital=10000.0,
        transaction_cost_pct=0.01,
        slippage_pct=0.0,
    )
    res = engine.run(df, AlwaysBuyStrategy())

    # Equity must decrease due to entry fee and marked-to-market exit fee
    assert res.final_equity < 10000.0
    assert res.total_cost_paid > 0.0


# ============================================================================
# 4. REGIME CLASSIFICATION & NO FUTURE LEAKAGE
# ============================================================================

def test_regime_classification_expanding_window():
    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    np.random.seed(42)
    close = 100.0 + np.cumsum(np.random.normal(0.5, 0.2, size=300))
    df = pd.DataFrame({
        "open": close - 0.2,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": [10000] * 300,
    }, index=dates)

    classified = RegimeClassifier.classify(df, trend_sma_window=50, vol_atr_window=14, min_history=30)
    
    valid_regimes = set(RegimeClassifier.REGIMES + ["Unclassified"])
    actual_regimes = set(classified["regime"].unique())
    assert actual_regimes.issubset(valid_regimes)

    late_regimes = classified["regime"].iloc[100:]
    assert "Bull / Low Volatility" in late_regimes.values


# ============================================================================
# 5. MULTI-ASSET ALIGNMENT & FORWARD-FILL INVARIANTS
# ============================================================================

def test_aligner_never_backfills():
    dates_crypto = pd.date_range("2023-01-01", periods=10, freq="D")
    dates_equity = pd.date_range("2023-01-01", periods=10, freq="B")
    
    df_crypto = pd.DataFrame({
        "open": [100.0 + i for i in range(10)],
        "high": [101.0 + i for i in range(10)],
        "low": [99.0 + i for i in range(10)],
        "close": [100.0 + i for i in range(10)],
        "volume": [500] * 10,
    }, index=dates_crypto)

    df_equity = pd.DataFrame({
        "open": [50.0 + i for i in range(len(dates_equity))],
        "high": [51.0 + i for i in range(len(dates_equity))],
        "low": [49.0 + i for i in range(len(dates_equity))],
        "close": [50.0 + i for i in range(len(dates_equity))],
        "volume": [1000] * len(dates_equity),
    }, index=dates_equity)

    raw_dfs = {"Bitcoin": df_crypto, "NVIDIA": df_equity}
    aligned_dfs, aligned_close, fill_stats = MultiAssetAligner.align(raw_dfs, calendar_mode="equity")

    assert len(aligned_close) == len(aligned_dfs["NVIDIA"])
    assert not aligned_close.isna().any().any()
    assert (aligned_close.index == aligned_dfs["NVIDIA"].index).all()

