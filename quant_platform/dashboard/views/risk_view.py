"""Tab 2: Returns & Risk - Volatility, Rolling Sharpe, and Drawdown Analytics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.indicators.returns import (
    calculate_daily_returns,
    calculate_cumulative_returns,
    calculate_rolling_returns,
)
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_drawdown_series,
    calculate_max_drawdown,
)
from quant_platform.dashboard.components import (
    get_asset_color,
    apply_plotly_theme,
)


def render_risk_view(aligned_close: pd.DataFrame, risk_free_rate: float = 0.04):
    st.markdown("### ⚡ Returns & Risk Analytics")
    st.markdown("Analyze asset risk profiles, historical volatility spikes, rolling Sharpe stability, and drawdowns.")

    daily_rets = calculate_daily_returns(aligned_close)
    cum_rets = calculate_cumulative_returns(daily_rets) * 100.0

    # Controls Row
    c1, c2 = st.columns([1, 1])
    with c1:
        rolling_window = st.slider("Rolling Window (Days)", min_value=15, max_value=252, value=60, step=5)
    with c2:
        risk_free_pct = st.number_input("Annual Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=risk_free_rate * 100.0, step=0.25)
        rf_rate = risk_free_pct / 100.0

    # 1. Cumulative Compound Returns Chart
    st.markdown("#### Cumulative Compound Returns (%)")
    fig_cum = go.Figure()
    for i, col in enumerate(cum_rets.columns):
        color = get_asset_color(col, i)
        fig_cum.add_trace(go.Scatter(
            x=cum_rets.index,
            y=cum_rets[col],
            name=col,
            line=dict(color=color, width=2.2),
            hovertemplate=f"<b>{col}</b>: %{{y:+.2f}}%<extra></extra>",
        ))
    apply_plotly_theme(fig_cum, title="Cumulative Compounding Return Paths", height=350)
    fig_cum.update_layout(yaxis_title="Return (%)")
    st.plotly_chart(fig_cum)

    # 2. Side-by-Side: Rolling Volatility & Rolling Sharpe Ratio
    col_v, col_s = st.columns(2)

    with col_v:
        st.markdown(f"#### Rolling {rolling_window}-Day Annualized Volatility (%)")
        fig_vol = go.Figure()
        for i, col in enumerate(daily_rets.columns):
            color = get_asset_color(col, i)
            roll_vol = calculate_annualized_volatility(daily_rets[col], periods_per_year=252, window=rolling_window) * 100.0
            fig_vol.add_trace(go.Scatter(
                x=roll_vol.index,
                y=roll_vol,
                name=col,
                line=dict(color=color, width=2.0),
            ))
        apply_plotly_theme(fig_vol, title=f"Rolling {rolling_window}D Annualized Volatility", height=320)
        fig_vol.update_layout(yaxis_title="Vol (%)")
        st.plotly_chart(fig_vol)

    with col_s:
        st.markdown(f"#### Rolling {rolling_window}-Day Annualized Sharpe Ratio")
        fig_shp = go.Figure()
        for i, col in enumerate(daily_rets.columns):
            color = get_asset_color(col, i)
            roll_shp = calculate_sharpe_ratio(daily_rets[col], risk_free_rate=rf_rate, periods_per_year=252, window=rolling_window)
            fig_shp.add_trace(go.Scatter(
                x=roll_shp.index,
                y=roll_shp,
                name=col,
                line=dict(color=color, width=2.0),
            ))
        fig_shp.add_hline(y=0.0, line_dash="dash", line_color="#4b5563")
        apply_plotly_theme(fig_shp, title=f"Rolling {rolling_window}D Sharpe Ratio", height=320)
        fig_shp.update_layout(yaxis_title="Sharpe Ratio")
        st.plotly_chart(fig_shp)

    # 3. Drawdown Series (Underwater Chart)
    st.markdown("---")
    st.markdown("#### 🌊 Underwater Drawdown Profiles (%)")
    fig_dd = go.Figure()
    for i, col in enumerate(aligned_close.columns):
        color = get_asset_color(col, i)
        dd = calculate_drawdown_series(aligned_close[col]) * 100.0
        # Convert hex to rgba for subtle fill
        fig_dd.add_trace(go.Scatter(
            x=dd.index,
            y=dd,
            name=f"{col} Drawdown",
            line=dict(color=color, width=1.5),
            fill='tozeroy',
            hovertemplate=f"<b>{col}</b>: %{{y:.2f}}%<extra></extra>",
        ))
    apply_plotly_theme(fig_dd, title="Historical Drawdown Depth from Peak", height=340)
    fig_dd.update_layout(yaxis_title="Drawdown (%)", yaxis=dict(ticksuffix="%"))
    st.plotly_chart(fig_dd)
