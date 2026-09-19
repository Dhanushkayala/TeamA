"""Unit tests for backtesting engine, no-lookahead guarantee, and strategy execution."""

import pytest
import pandas as pd
import numpy as np

from quant_platform.backtest.strategies import (
    SMACrossoverStrategy,
    EMATrendStrategy,
    MomentumStrategy,
    MeanReversionStrategy,
)
from quant_platform.backtest.engine import BacktestEngine, Trade
from quant_platform.backtest.robustness import (
    run_parameter_sweep_ma,
    run_cost_sensitivity,
    run_train_test_split,
)


@pytest.fixture
def synthetic_ohlcv():
    dates = pd.date_range("2022-01-01", periods=200, freq="B")
    np.random.seed(42)
    # Upward trend followed by downward trend
    trend = np.concatenate([np.linspace(100, 150, 100), np.linspace(150, 90, 100)])
    noise = np.random.normal(0, 1.5, 200)
    close = trend + noise
    open_p = close + np.random.normal(0, 0.5, 200)
    high = np.maximum(open_p, close) + np.abs(np.random.normal(0, 1.0, 200))
    low = np.minimum(open_p, close) - np.abs(np.random.normal(0, 1.0, 200))
    vol = np.random.uniform(1000, 5000, 200)

    df = pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": vol,
    }, index=dates)
    return df


def test_strategies_signal_generation(synthetic_ohlcv):
    sma = SMACrossoverStrategy(fast_period=10, slow_period=30)
    sig_sma = sma.generate_signals(synthetic_ohlcv)
    assert set(sig_sma.unique()).issubset({0.0, 1.0})
    assert len(sig_sma) == len(synthetic_ohlcv)

    ema = EMATrendStrategy(fast_span=10, slow_span=30)
    sig_ema = ema.generate_signals(synthetic_ohlcv)
    assert set(sig_ema.unique()).issubset({0.0, 1.0})

    mom = MomentumStrategy(lookback=20, threshold_pct=0.0)
    sig_mom = mom.generate_signals(synthetic_ohlcv)
    assert set(sig_mom.unique()).issubset({0.0, 1.0})

    mr = MeanReversionStrategy(lookback=15, entry_z=-1.0, exit_z=0.0)
    sig_mr = mr.generate_signals(synthetic_ohlcv)
    assert set(sig_mr.unique()).issubset({0.0, 1.0})


def test_no_lookahead_bias_guarantee():
    """
    CRITICAL TEST:
    A sharp price spike on day t that triggers a buy signal must NOT allow the portfolio
    to capture the day t return. The trade executes on day t+1.
    """
    dates = pd.date_range("2023-01-01", periods=5, freq="B")
    # Day 0: 100
    # Day 1: 100
    # Day 2: 200 (Huge 100% surge on Day 2 triggers signal on Day 2 close)
    # Day 3: 200 (Flat)
    # Day 4: 200 (Flat)
    df = pd.DataFrame({
        "open": [100.0, 100.0, 200.0, 200.0, 200.0],
        "high": [101.0, 101.0, 205.0, 201.0, 201.0],
        "low": [99.0, 99.0, 100.0, 199.0, 199.0],
        "close": [100.0, 100.0, 200.0, 200.0, 200.0],
        "volume": [1000] * 5,
    }, index=dates)

    class TriggerOnSpikeStrategy(SMACrossoverStrategy):
        def generate_signals(self, d):
            # Emits signal 1 on day 2 when close == 200
            s = pd.Series(0.0, index=d.index)
            s.iloc[2] = 1.0  # signal generated at close of day 2
            return s

    engine = BacktestEngine(initial_capital=10000.0, transaction_cost_pct=0.0, slippage_pct=0.0)
    res = engine.run(df, TriggerOnSpikeStrategy())

    # Day 0, Day 1, Day 2 equity MUST remain initial capital ($10,000) because position was 0
    # Day 2 price surge was missed because signal only executes at Day 3
    assert res.equity_curve.iloc[0] == 10000.0
    assert res.equity_curve.iloc[1] == 10000.0
    assert res.equity_curve.iloc[2] == 10000.0
    # On day 3, bought at 200, closed at 200 -> equity is still 10000
    assert res.equity_curve.iloc[3] == 10000.0
    assert res.positions.iloc[2] == 0.0  # position at day 2 is still 0
    assert res.positions.iloc[3] == 1.0  # position at day 3 is 1


def test_transaction_cost_deduction():
    dates = pd.date_range("2023-01-01", periods=4, freq="B")
    # Flat price 100 across 4 days
    df = pd.DataFrame({
        "open": [100.0, 100.0, 100.0, 100.0],
        "high": [100.0, 100.0, 100.0, 100.0],
        "low": [100.0, 100.0, 100.0, 100.0],
        "close": [100.0, 100.0, 100.0, 100.0],
        "volume": [1000] * 4,
    }, index=dates)

    class InOutStrategy(SMACrossoverStrategy):
        def generate_signals(self, d):
            s = pd.Series(0.0, index=d.index)
            s.iloc[0] = 1.0  # Buy on day 1
            s.iloc[1] = 0.0  # Exit on day 2
            return s

    # 1% transaction cost, 0 slippage
    engine = BacktestEngine(initial_capital=10000.0, transaction_cost_pct=0.01, slippage_pct=0.0)
    res = engine.run(df, InOutStrategy())

    # Equity after 1 round-trip on flat price must be less than starting capital due to fees
    assert res.final_equity < 10000.0
    assert res.total_cost_paid > 0.0
    assert len(res.trades) >= 1


def test_robustness_modules(synthetic_ohlcv):
    # Parameter sweep
    sharpe_mat, ret_mat = run_parameter_sweep_ma(
        synthetic_ohlcv,
        strategy_type="SMA",
        fast_range=[5, 10],
        slow_range=[20, 30],
    )
    assert sharpe_mat.shape == (2, 2)
    assert not sharpe_mat.isna().all().all()

    # Cost sensitivity
    strat = SMACrossoverStrategy(fast_period=10, slow_period=30)
    cost_df = run_cost_sensitivity(synthetic_ohlcv, strat, cost_range=[0.0, 0.001, 0.005])
    assert len(cost_df) == 3
    assert "Sharpe Ratio" in cost_df.columns

    # Train/Test split
    tt = run_train_test_split(synthetic_ohlcv, strat, train_ratio=0.7)
    assert "train_metrics" in tt
    assert "test_metrics" in tt
    assert "split_date" in tt
