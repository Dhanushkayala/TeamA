"""Quantitative Indicators Module."""

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

__all__ = [
    "calculate_sma",
    "calculate_ema",
    "calculate_daily_returns",
    "calculate_log_returns",
    "calculate_cumulative_returns",
    "calculate_rolling_returns",
    "calculate_volatility",
    "calculate_annualized_volatility",
    "calculate_sharpe_ratio",
    "calculate_drawdown_series",
    "calculate_max_drawdown",
    "calculate_cagr",
    "calculate_atr",
    "calculate_bollinger_bands",
    "calculate_zscore",
]
