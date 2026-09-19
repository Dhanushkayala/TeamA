"""Tab 2: Returns & Risk - Volatility, Rolling Sharpe, and Drawdown Analytics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.indicators.returns import (
    calculate_daily_returns,
    calculate_cumulative_returns,
)
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_drawdown_series,
    calculate_max_drawdown,
    calculate_cagr,
    calculate_calmar_ratio,
)
from quant_platform.dashboard.components import (
    get_asset_color,
    apply_plotly_theme,
    render_section_banner,
)


def render_risk_view(aligned_close: pd.DataFrame, risk_free_rate: float = 0.04):
    render_section_banner(
        icon="",
        title="Returns & Risk Distribution Analytics",
        subtitle="Analyze volatility clustering, tail risk, rolling Sharpe stability, and drawdown depths across the universe.",
        badge_text="Risk Suite Active",
        badge_color="#f59e0b",
    )

    daily_rets = calculate_daily_returns(aligned_close).dropna()
    cum_rets = calculate_cumulative_returns(daily_rets) * 100.0

    # Controls Row
    c1, c2 = st.columns([1, 1])
    with c1:
        rolling_window = st.slider("Rolling Window (Days)", min_value=15, max_value=252, value=60, step=5)
    with c2:
        risk_free_pct = st.number_input("Annual Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=risk_free_rate * 100.0, step=0.25)
        rf_rate = risk_free_pct / 100.0

    # 1. Row of Risk Scorecards per Asset
    risk_cols = st.columns(len(aligned_close.columns))
    for i, col in enumerate(aligned_close.columns):
        s = aligned_close[col].dropna()
        r = daily_rets[col]
        vol = calculate_annualized_volatility(r, periods_per_year=252) * 100.0
        shp = calculate_sharpe_ratio(r, risk_free_rate=rf_rate, periods_per_year=252)
        sortino = calculate_sortino_ratio(r, risk_free_rate=rf_rate, periods_per_year=252)
        mdd = calculate_max_drawdown(s) * 100.0
        cagr = calculate_cagr(s, periods_per_year=252) * 100.0
        calmar = calculate_calmar_ratio(cagr / 100.0, mdd / 100.0)
        color = get_asset_color(col, i)

        with risk_cols[i]:
            st.markdown(f"""
            <div class="quant-card" style="border-top: 3px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-weight:700; color:var(--text-primary); font-size:0.90rem;">{col}</span>
                    <span style="font-size:0.75rem; color:{color}; font-weight:700; font-family:'JetBrains Mono',monospace;">Vol {vol:.1f}%</span>
                </div>
                <div style="font-size:1.45rem; font-weight:800; color:var(--text-primary); font-family:'JetBrains Mono',monospace;">
                    Sharpe {shp:.2f}
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:8px; padding-top:6px; border-top:1px solid var(--border-subtle); font-size:0.78rem; color:var(--text-secondary); font-family:'JetBrains Mono',monospace;">
                    <span>Sortino: <strong style="color:var(--text-primary);">{sortino:.2f}</strong></span>
                    <span>Calmar: <strong style="color:var(--text-primary);">{calmar:.2f}</strong></span>
                </div>
                <div style="font-size:0.74rem; color:#f43f5e; margin-top:4px; font-family:'JetBrains Mono',monospace;">
                    Max Drawdown: {mdd:.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. Cumulative Compound Returns Chart
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Cumulative Compounding Growth Paths (%)")
    fig_cum = go.Figure()
    for i, col in enumerate(cum_rets.columns):
        color = get_asset_color(col, i)
        fig_cum.add_trace(go.Scatter(
            x=cum_rets.index,
            y=cum_rets[col],
            name=col,
            line=dict(color=color, width=2.4),
            hovertemplate=f"<b>{col}</b>: %{{y:+.2f}}%<extra></extra>",
        ))
    apply_plotly_theme(fig_cum, title="Cumulative Compounding Return Trajectories", height=360)
    fig_cum.update_layout(yaxis_title="Return (%)")
    st.plotly_chart(fig_cum, use_container_width=True)

    # 3. Side-by-Side: Rolling Volatility & Rolling Sharpe Ratio
    st.markdown("---")
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
        apply_plotly_theme(fig_vol, title=f"Rolling {rolling_window}D Volatility Spike Profile", height=330)
        fig_vol.update_layout(yaxis_title="Vol (%)")
        st.plotly_chart(fig_vol, use_container_width=True)

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
        fig_shp.add_hline(y=0.0, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        apply_plotly_theme(fig_shp, title=f"Rolling {rolling_window}D Risk-Adjusted Sharpe", height=330)
        fig_shp.update_layout(yaxis_title="Sharpe Ratio")
        st.plotly_chart(fig_shp, use_container_width=True)

    # 4. Drawdown Series (Underwater Chart)
    st.markdown("---")
    st.markdown("####  Underwater Drawdown Profiles (%)")
    fig_dd = go.Figure()
    for i, col in enumerate(aligned_close.columns):
        color = get_asset_color(col, i)
        dd = calculate_drawdown_series(aligned_close[col]) * 100.0
        fig_dd.add_trace(go.Scatter(
            x=dd.index,
            y=dd,
            name=f"{col} Drawdown",
            line=dict(color=color, width=1.6),
            fill='tozeroy',
            hovertemplate=f"<b>{col}</b>: %{{y:.2f}}%<extra></extra>",
        ))
    apply_plotly_theme(fig_dd, title="Peak-to-Trough Capital Degradation Depth", height=340)
    fig_dd.update_layout(yaxis_title="Drawdown (%)", yaxis=dict(ticksuffix="%"))
    st.plotly_chart(fig_dd, use_container_width=True)
