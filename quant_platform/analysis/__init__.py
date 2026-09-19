"""Analysis package init."""

from quant_platform.analysis.correlation import (
    calculate_correlation_matrix,
    calculate_rolling_correlation,
    calculate_all_rolling_correlations,
)
from quant_platform.analysis.regimes import RegimeClassifier

__all__ = [
    "calculate_correlation_matrix",
    "calculate_rolling_correlation",
    "calculate_all_rolling_correlations",
    "RegimeClassifier",
]

