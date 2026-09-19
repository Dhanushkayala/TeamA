"""Dashboard view modules."""

from quant_platform.dashboard.views.overview_view import render_overview_view
from quant_platform.dashboard.views.risk_view import render_risk_view
from quant_platform.dashboard.views.correlation_view import render_correlation_view
from quant_platform.dashboard.views.backtest_view import render_backtest_view
from quant_platform.dashboard.views.robustness_view import render_robustness_view
from quant_platform.dashboard.views.regime_view import render_regime_view
from quant_platform.dashboard.views.ai_view import render_ai_view
from quant_platform.dashboard.views.profile_view import render_profile_view

__all__ = [
    "render_overview_view",
    "render_risk_view",
    "render_correlation_view",
    "render_backtest_view",
    "render_robustness_view",
    "render_regime_view",
    "render_ai_view",
    "render_profile_view",
]
