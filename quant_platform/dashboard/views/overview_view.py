"""Tab 1: Overview - Price trends, technical overlays, and headline quantitative metrics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.indicators.moving_averages import calculate_sma, calculate_ema
from quant_platform.indicators.oscillators import calculate_bollinger_bands
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
)
from quant_platform.dashboard.components import (
    get_asset_color,
    apply_plotly_theme,
    render_metric_card,
)


def render_overview_view(
    aligned_dfs: dict,
    aligned_close: pd.DataFrame,
    fill_stats: dict,
    risk_free_rate: float = 0.04,
):
    st.markdown("### 📈 Multi-Asset Intelligence & Technical Overview")
    st.markdown("Comparative performance, asset health, and moving average overlays normalized on a common calendar.")

    # 1. Row of Headline Metric Cards per Asset
    cols = st.columns(len(aligned_close.columns))
    for i, asset_name in enumerate(aligned_close.columns):
        close_s = aligned_close[asset_name]
        daily_ret = close_s.pct_change().dropna()
        tot_ret = ((close_s.iloc[-1] / close_s.iloc[0]) - 1.0) * 100.0
        ann_vol = calculate_annualized_volatility(daily_ret, periods_per_year=252) * 100.0
        sharpe = calculate_sharpe_ratio(daily_ret, risk_free_rate=risk_free_rate, periods_per_year=252)
        mdd = calculate_max_drawdown(close_s) * 100.0

        with cols[i]:
            color = get_asset_color(asset_name, i)
            delta_str = f"{tot_ret:+.1f}%"
            delta_color = "positive" if tot_ret >= 0 else "negative"
            
            st.markdown(f"""
            <div class="quant-card" style="border-top: 3px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="quant-card-title">{asset_name}</span>
                    <span style="font-size:0.75rem; color:{color}; font-weight:600;">{delta_str}</span>
                </div>
                <div class="quant-card-value">Sharpe {sharpe:.2f}</div>
                <div class="quant-card-sub">Vol {ann_vol:.1f}% · MDD {mdd:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    # 2. Normalized Price Chart (Base 100)
    st.markdown("#### Normalized Performance (Base = 100)")
    norm_df = (aligned_close / aligned_close.iloc[0]) * 100.0

    fig_norm = go.Figure()
    for i, col in enumerate(norm_df.columns):
        color = get_asset_color(col, i)
        fig_norm.add_trace(go.Scatter(
            x=norm_df.index,
            y=norm_df[col],
            name=col,
            line=dict(color=color, width=2.5),
            hovertemplate=f"<b>{col}</b>: %{{y:.2f}}<extra></extra>",
        ))
    apply_plotly_theme(fig_norm, title="Normalized Cumulative Price Path (Base = 100)", height=380)
    fig_norm.update_layout(yaxis_title="Index Value ($100 Base)")
    st.plotly_chart(fig_norm)

    # 3. Individual Asset Technical Analysis with Moving Averages & Bands
    st.markdown("---")
    st.markdown("#### 🔬 Detailed Asset Chart & Indicator Overlays")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        selected_asset = st.selectbox("Select Asset for Inspection", list(aligned_close.columns), index=0)
    with col_sel2:
        overlays = st.multiselect(
            "Select Technical Overlays",
            ["SMA 20", "SMA 50", "SMA 200", "EMA 21", "EMA 55", "Bollinger Bands (20, 2)"],
            default=["SMA 50", "SMA 200"],
        )

    asset_df = aligned_dfs[selected_asset]
    close_series = asset_df["close"]
    asset_color = get_asset_color(selected_asset)

    fig_tech = go.Figure()
    # Main Close Price
    fig_tech.add_trace(go.Scatter(
        x=asset_df.index,
        y=close_series,
        name=f"{selected_asset} Close",
        line=dict(color=asset_color, width=2.5),
    ))

    # Overlays
    if "SMA 20" in overlays:
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index,
            y=calculate_sma(close_series, 20),
            name="SMA 20",
            line=dict(color="#38bdf8", width=1.5, dash="dot"),
        ))
    if "SMA 50" in overlays:
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index,
            y=calculate_sma(close_series, 50),
            name="SMA 50",
            line=dict(color="#a855f7", width=1.8),
        ))
    if "SMA 200" in overlays:
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index,
            y=calculate_sma(close_series, 200),
            name="SMA 200",
            line=dict(color="#f43f5e", width=2.0),
        ))
    if "EMA 21" in overlays:
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index,
            y=calculate_ema(close_series, 21),
            name="EMA 21",
            line=dict(color="#2dd4bf", width=1.5, dash="dash"),
        ))
    if "EMA 55" in overlays:
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index,
            y=calculate_ema(close_series, 55),
            name="EMA 55",
            line=dict(color="#fb923c", width=1.5, dash="dash"),
        ))
    if "Bollinger Bands (20, 2)" in overlays:
        mid, upper, lower = calculate_bollinger_bands(close_series, window=20, num_std=2.0)
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index, y=upper, name="Upper BB",
            line=dict(color="rgba(156, 163, 175, 0.4)", width=1),
        ))
        fig_tech.add_trace(go.Scatter(
            x=asset_df.index, y=lower, name="Lower BB",
            fill='tonexty', fillcolor='rgba(156, 163, 175, 0.08)',
            line=dict(color="rgba(156, 163, 175, 0.4)", width=1),
        ))

    apply_plotly_theme(fig_tech, title=f"{selected_asset} Price with Selected Indicators", height=420)
    fig_tech.update_layout(yaxis_title="Price ($)")
    st.plotly_chart(fig_tech)

    # Missing Bar / Data Health Summary
    with st.expander("ℹ️ Data Alignment & Forward-Fill Diagnostics"):
        diag_cols = st.columns(len(aligned_dfs))
        for i, (name, count) in enumerate(fill_stats.items()):
            with diag_cols[i]:
                st.metric(label=f"{name} Non-Trading Day Fills", value=f"{count} bars", help="Forward-filled bars to sync on the unified trading calendar.")
