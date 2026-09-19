"""Robustness analysis: parameter sweeps, cost sensitivity, and train/test validation."""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from quant_platform.backtest.strategies import SMACrossoverStrategy, EMATrendStrategy
from quant_platform.backtest.engine import BacktestEngine


def run_parameter_sweep_ma(
    df: pd.DataFrame,
    strategy_type: str = "SMA",
    fast_range: Optional[List[int]] = None,
    slow_range: Optional[List[int]] = None,
    transaction_cost_pct: float = 0.0010,
    periods_per_year: int = 252,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run 2D parameter grid sweep over Fast & Slow MA periods.

    Returns:
        sharpe_matrix: DataFrame with slow_periods as rows, fast_periods as columns, containing Sharpe values.
        return_matrix: DataFrame containing Total Return (%) values.
    """
    if fast_range is None:
        fast_range = [5, 10, 15, 20, 30, 50]
    if slow_range is None:
        slow_range = [30, 50, 75, 100, 150, 200]

    sharpe_matrix = pd.DataFrame(index=slow_range, columns=fast_range, dtype=float)
    return_matrix = pd.DataFrame(index=slow_range, columns=fast_range, dtype=float)

    engine = BacktestEngine(
        initial_capital=100000.0,
        transaction_cost_pct=transaction_cost_pct,
        periods_per_year=periods_per_year,
    )

    for slow in slow_range:
        for fast in fast_range:
            if fast >= slow:
                sharpe_matrix.loc[slow, fast] = np.nan
                return_matrix.loc[slow, fast] = np.nan
                continue

            if strategy_type == "EMA":
                strat = EMATrendStrategy(fast_span=fast, slow_span=slow)
            else:
                strat = SMACrossoverStrategy(fast_period=fast, slow_period=slow)

            res = engine.run(df, strat)
            sharpe_matrix.loc[slow, fast] = res.metrics["Strategy"]["Sharpe Ratio"]
            return_matrix.loc[slow, fast] = res.metrics["Strategy"]["Total Return (%)"]

    return sharpe_matrix, return_matrix


def run_cost_sensitivity(
    df: pd.DataFrame,
    strategy,
    cost_range: Optional[List[float]] = None,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    """
    Test performance sensitivity across a range of transaction fee levels (e.g., 0% to 1.0%).
    """
    if cost_range is None:
        cost_range = [0.0, 0.0005, 0.0010, 0.0020, 0.0035, 0.0050, 0.0075, 0.0100]

    rows = []
    for cost in cost_range:
        engine = BacktestEngine(
            initial_capital=100000.0,
            transaction_cost_pct=cost,
            periods_per_year=periods_per_year,
        )
        res = engine.run(df, strategy)
        strat_m = res.metrics["Strategy"]
        rows.append({
            "Cost (%)": round(cost * 100, 3),
            "Cost (bps)": round(cost * 10000, 1),
            "Total Return (%)": strat_m["Total Return (%)"],
            "CAGR (%)": strat_m["CAGR (%)"],
            "Sharpe Ratio": strat_m["Sharpe Ratio"],
            "Max Drawdown (%)": strat_m["Max Drawdown (%)"],
            "Total Fees Paid ($)": strat_m["Total Costs Paid ($)"],
        })

    return pd.DataFrame(rows)


def run_train_test_split(
    df: pd.DataFrame,
    strategy,
    train_ratio: float = 0.70,
    transaction_cost_pct: float = 0.0010,
    periods_per_year: int = 252,
) -> Dict[str, Any]:
    """
    Split data chronologically into In-Sample (Train) and Out-of-Sample (Test) sets
    to evaluate overfitting and strategy decay.
    """
    split_idx = int(len(df) * train_ratio)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    engine = BacktestEngine(
        initial_capital=100000.0,
        transaction_cost_pct=transaction_cost_pct,
        periods_per_year=periods_per_year,
    )

    train_res = engine.run(train_df, strategy)
    test_res = engine.run(test_df, strategy)

    return {
        "split_date": df.index[split_idx].strftime("%Y-%m-%d"),
        "train_range": f"{train_df.index[0].strftime('%Y-%m-%d')} to {train_df.index[-1].strftime('%Y-%m-%d')}",
        "test_range": f"{test_df.index[0].strftime('%Y-%m-%d')} to {test_df.index[-1].strftime('%Y-%m-%d')}",
        "train_metrics": train_res.metrics["Strategy"],
        "test_metrics": test_res.metrics["Strategy"],
        "train_res": train_res,
        "test_res": test_res,
    }
