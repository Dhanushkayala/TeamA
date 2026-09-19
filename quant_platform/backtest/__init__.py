"""Backtesting Engine, Strategies, Robustness Analysis, and Performance Metrics."""

from quant_platform.backtest.strategies import (
    BaseStrategy,
    SMACrossoverStrategy,
    EMATrendStrategy,
    MomentumStrategy,
    MeanReversionStrategy,
    STRATEGY_REGISTRY,
)
from quant_platform.backtest.engine import BacktestEngine, BacktestResult, Trade
from quant_platform.backtest.metrics import calculate_performance_summary
from quant_platform.backtest.robustness import (
    run_parameter_sweep_ma,
    run_cost_sensitivity,
    run_train_test_split,
)

__all__ = [
    "BaseStrategy",
    "SMACrossoverStrategy",
    "EMATrendStrategy",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "STRATEGY_REGISTRY",
    "BacktestEngine",
    "BacktestResult",
    "Trade",
    "calculate_performance_summary",
    "run_parameter_sweep_ma",
    "run_cost_sensitivity",
    "run_train_test_split",
]
