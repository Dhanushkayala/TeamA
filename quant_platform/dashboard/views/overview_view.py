"""Tab 1: Overview - Price trends, technical overlays, and headline quantitative metrics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    st.markdown("Comparative multi-asset performance, risk-return positioning, and technical overlays normalized on a common calendar.")

    # Compute asset summary statistics
    asset_stats = []
    for i, asset_name in enumerate(aligned_close.columns):
        close_s = aligned_close[asset_name].dropna()
        if len(close_s) < 2:
            continue
        daily_ret = close_s.pct_change().dropna()
        tot_ret = ((close_s.iloc[-1] / close_s.iloc[0]) - 1.0) * 100.0
        ann_vol = calculate_annualized_volatility(daily_ret, periods_per_year=252) * 100.0
        sharpe = calculate_sharpe_ratio(daily_ret, risk_free_rate=risk_free_rate, periods_per_year=252)
        mdd = calculate_max_drawdown(close_s) * 100.0
        asset_stats.append({
            "Asset": asset_name,
            "Total Return (%)": tot_ret,
            "Annualized Vol (%)": ann_vol,
            "Sharpe Ratio": sharpe,
            "Max Drawdown (%)": mdd,
            "Color": get_asset_color(asset_name, i),
        })

    stats_df = pd.DataFrame(asset_stats)

    # 1. Headline Metric Cards Row
    cols = st.columns(len(aligned_close.columns))
    for i, row in stats_df.iterrows():
        with cols[i]:
            color = row["Color"]
            delta_str = f"{row['Total Return (%)']:+.1f}%"
            st.markdown(f"""
            <div class="quant-card" style="border-top: 3px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="quant-card-title">{row['Asset']}</span>
                    <span style="font-size:0.78rem; color:{color}; font-weight:700;">{delta_str}</span>
                </div>
                <div class="quant-card-value">Sharpe {row['Sharpe Ratio']:.2f}</div>
                <div class="quant-card-sub">Vol {row['Annualized Vol (%)']:.1f}% · MDD {row['Max Drawdown (%)']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 2. Side-by-Side: Normalized Cumulative Price Path & Risk-Return Scatter
    col_chart1, col_chart2 = st.columns([1.2, 1.0])

    with col_chart1:
        st.markdown("#### 🚀 Normalized Growth ($100 Base)")
        norm_df = (aligned_close / aligned_close.iloc[0]) * 100.0
        fig_norm = go.Figure()
        for i, col in enumerate(norm_df.columns):
            color = get_asset_color(col, i)
            fig_norm.add_trace(go.Scatter(
                x=norm_df.index,
                y=norm_df[col],
                name=col,
                line=dict(color=color, width=2.4),
                hovertemplate=f"<b>{col}</b>: $%{{y:.2f}}<extra></extra>",
            ))
        apply_plotly_theme(fig_norm, title="Normalized Cumulative Price ($100 Base)", height=340)
        fig_norm.update_layout(yaxis_title="Index Value ($)")
        st.plotly_chart(fig_norm, use_container_width=True)

    with col_chart2:
        st.markdown("#### 🎯 Risk vs. Return Positioning")
        fig_bubble = go.Figure()
        for _, row in stats_df.iterrows():
            bubble_size = max(float(row["Sharpe Ratio"]) * 14 + 16, 12)
            fig_bubble.add_trace(go.Scatter(
                x=[row["Annualized Vol (%)"]],
                y=[row["Total Return (%)"]],
                mode="markers+text",
                name=row["Asset"],
                text=[f"<b>{row['Asset']}</b>"],
                textposition="top center",
                textfont=dict(color="#e6edf3", size=11),
                marker=dict(
                    size=bubble_size,
                    color=row["Color"],
                    opacity=0.85,
                    line=dict(width=1.5, color="#ffffff"),
                ),
                hovertemplate=(
                    f"<b>{row['Asset']}</b><br>"
                    f"Total Return: {row['Total Return (%)']:+.2f}%<br>"
                    f"Annual Volatility: {row['Annualized Vol (%)']:.2f}%<br>"
                    f"Sharpe Ratio: {row['Sharpe Ratio']:.2f}<br>"
                    f"Max Drawdown: {row['Max Drawdown (%)']:.2f}%<extra></extra>"
                ),
            ))
        fig_bubble.add_hline(y=0.0, line_dash="dash", line_color="#484f58", line_width=1)
        apply_plotly_theme(fig_bubble, title="Bubble size ∝ Sharpe Ratio", height=340)
        fig_bubble.update_layout(
            xaxis_title="Annualized Volatility (%)",
            yaxis_title="Total Return (%)",
            showlegend=False,
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    # 3. Multi-Asset Comparative Bar Breakdown
    st.markdown("---")
    st.markdown("#### 📊 Comparative Risk-Adjusted Bar Breakdown")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        fig_bar_ret = go.Figure()
        fig_bar_ret.add_trace(go.Bar(
            x=stats_df["Asset"],
            y=stats_df["Total Return (%)"],
            marker_color=stats_df["Color"],
            text=[f"{v:+.1f}%" for v in stats_df["Total Return (%)"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b>: %{y:+.2f}%<extra></extra>",
        ))
        apply_plotly_theme(fig_bar_ret, title="Total Cumulative Return (%)", height=270)
        fig_bar_ret.update_layout(yaxis_title="Return (%)", showlegend=False)
        st.plotly_chart(fig_bar_ret, use_container_width=True)

    with col_b2:
        fig_bar_shp = go.Figure()
        fig_bar_shp.add_trace(go.Bar(
            x=stats_df["Asset"],
            y=stats_df["Sharpe Ratio"],
            marker_color=stats_df["Color"],
            text=[f"{v:.2f}" for v in stats_df["Sharpe Ratio"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b>: Sharpe %{y:.2f}<extra></extra>",
        ))
        fig_bar_shp.add_hline(y=1.0, line_dash="dash", line_color="#10b981", annotation_text="Benchmark Sharpe (1.0)", annotation_position="top right")
        apply_plotly_theme(fig_bar_shp, title="Annualized Sharpe Ratio", height=270)
        fig_bar_shp.update_layout(yaxis_title="Sharpe Ratio", showlegend=False)
        st.plotly_chart(fig_bar_shp, use_container_width=True)

    # 4. Individual Asset Technical Analysis with Moving Averages & Volume Subplot
    st.markdown("---")
    st.markdown("#### 🔬 Detailed Technical Price & Volume Overlays")
    
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
    has_volume = "volume" in asset_df.columns and (asset_df["volume"] > 0).any()
    asset_color = get_asset_color(selected_asset)

    if has_volume:
        fig_tech = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            row_heights=[0.75, 0.25],
        )
    else:
        fig_tech = go.Figure()

    # Main Close Price Trace
    main_trace = go.Scatter(
        x=asset_df.index,
        y=close_series,
        name=f"{selected_asset} Close",
        line=dict(color=asset_color, width=2.4),
        hovertemplate="<b>Close</b>: $%{y:.2f}<extra></extra>",
    )

    if has_volume:
        fig_tech.add_trace(main_trace, row=1, col=1)
    else:
        fig_tech.add_trace(main_trace)

    # Technical Indicator Overlays
    indicator_traces = []
    if "SMA 20" in overlays:
        indicator_traces.append((calculate_sma(close_series, 20), "SMA 20", "#38bdf8", "dot", 1.5))
    if "SMA 50" in overlays:
        indicator_traces.append((calculate_sma(close_series, 50), "SMA 50", "#a855f7", "solid", 1.8))
    if "SMA 200" in overlays:
        indicator_traces.append((calculate_sma(close_series, 200), "SMA 200", "#f43f5e", "solid", 2.0))
    if "EMA 21" in overlays:
        indicator_traces.append((calculate_ema(close_series, 21), "EMA 21", "#2dd4bf", "dash", 1.5))
    if "EMA 55" in overlays:
        indicator_traces.append((calculate_ema(close_series, 55), "EMA 55", "#fb923c", "dash", 1.5))

    for series, label, color, dash, width in indicator_traces:
        t = go.Scatter(
            x=asset_df.index, y=series, name=label,
            line=dict(color=color, width=width, dash=dash),
            hovertemplate=f"<b>{label}</b>: $%{{y:.2f}}<extra></extra>",
        )
        if has_volume:
            fig_tech.add_trace(t, row=1, col=1)
        else:
            fig_tech.add_trace(t)

    if "Bollinger Bands (20, 2)" in overlays:
        mid, upper, lower = calculate_bollinger_bands(close_series, window=20, num_std=2.0)
        u_trace = go.Scatter(
            x=asset_df.index, y=upper, name="Upper BB",
            line=dict(color="rgba(156, 163, 175, 0.4)", width=1),
        )
        l_trace = go.Scatter(
            x=asset_df.index, y=lower, name="Lower BB",
            fill='tonexty', fillcolor='rgba(156, 163, 175, 0.08)',
            line=dict(color="rgba(156, 163, 175, 0.4)", width=1),
        )
        if has_volume:
            fig_tech.add_trace(u_trace, row=1, col=1)
            fig_tech.add_trace(l_trace, row=1, col=1)
        else:
            fig_tech.add_trace(u_trace)
            fig_tech.add_trace(l_trace)

    # Volume Sub-chart
    if has_volume:
        vol_colors = np.where(asset_df["close"] >= asset_df["open"], "rgba(34, 197, 94, 0.6)", "rgba(239, 68, 68, 0.6)")
        fig_tech.add_trace(go.Bar(
            x=asset_df.index,
            y=asset_df["volume"],
            name="Volume",
            marker_color=vol_colors,
            hovertemplate="<b>Volume</b>: %{y:,.0f}<extra></extra>",
        ), row=2, col=1)

    apply_plotly_theme(fig_tech, title=f"{selected_asset} Historical Price & Indicator Trajectory", height=440)
    if has_volume:
        fig_tech.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig_tech.update_yaxes(title_text="Volume", row=2, col=1)
    else:
        fig_tech.update_layout(yaxis_title="Price ($)")

    st.plotly_chart(fig_tech, use_container_width=True)

    # Missing Bar / Data Health Summary
    with st.expander("ℹ️ Multi-Asset Alignment & Forward-Fill Diagnostics"):
        diag_cols = st.columns(len(aligned_dfs))
        for i, (name, count) in enumerate(fill_stats.items()):
            with diag_cols[i]:
                st.metric(
                    label=f"{name} Trading Fills",
                    value=f"{count} bars",
                    help="Forward-filled bars to sync on the unified calendar.",
                )
