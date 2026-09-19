"""Tab 2: Returns & Risk - Volatility, Rolling Sharpe, Distribution, and Drawdown Analytics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

from quant_platform.indicators.returns import (
    calculate_daily_returns,
    calculate_cumulative_returns,
    calculate_rolling_returns,
)
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_downside_deviation,
    calculate_drawdown_series,
    calculate_max_drawdown,
)
from quant_platform.dashboard.components import (
    get_asset_color,
    apply_plotly_theme,
)


def render_risk_view(aligned_close: pd.DataFrame, risk_free_rate: float = 0.04):
    st.markdown("### ⚡ Returns & Risk Analytics")
    st.markdown("Explore risk distributions, tail risk fatness, rolling Sharpe stability, and peak-to-trough drawdowns.")

    daily_rets = calculate_daily_returns(aligned_close).dropna()
    cum_rets = calculate_cumulative_returns(daily_rets) * 100.0

    # Controls Row
    c1, c2 = st.columns([1, 1])
    with c1:
        rolling_window = st.slider("Rolling Window (Days)", min_value=15, max_value=252, value=60, step=5)
    with c2:
        risk_free_pct = st.number_input("Annual Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=risk_free_rate * 100.0, step=0.25)
        rf_rate = risk_free_pct / 100.0

    # 1. Cumulative Compound Returns Chart
    st.markdown("#### 📈 Cumulative Compound Returns (%)")
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
    apply_plotly_theme(fig_cum, title="Cumulative Compounding Growth Trajectory", height=340)
    fig_cum.update_layout(yaxis_title="Return (%)")
    st.plotly_chart(fig_cum, use_container_width=True)

    # 2. Side-by-Side: Rolling Volatility & Rolling Sharpe Ratio
    col_v, col_s = st.columns(2)

    with col_v:
        st.markdown(f"#### 🌊 Rolling {rolling_window}D Annualized Volatility (%)")
        fig_vol = go.Figure()
        for i, col in enumerate(daily_rets.columns):
            color = get_asset_color(col, i)
            roll_vol = calculate_annualized_volatility(daily_rets[col], periods_per_year=252, window=rolling_window) * 100.0
            fig_vol.add_trace(go.Scatter(
                x=roll_vol.index,
                y=roll_vol,
                name=col,
                line=dict(color=color, width=2.0),
                hovertemplate=f"<b>{col}</b>: %{{y:.2f}}%<extra></extra>",
            ))
        apply_plotly_theme(fig_vol, title=f"Rolling {rolling_window}D Annualized Volatility", height=300)
        fig_vol.update_layout(yaxis_title="Vol (%)")
        st.plotly_chart(fig_vol, use_container_width=True)

    with col_s:
        st.markdown(f"#### 🎯 Rolling {rolling_window}D Sharpe Ratio")
        fig_shp = go.Figure()
        for i, col in enumerate(daily_rets.columns):
            color = get_asset_color(col, i)
            roll_shp = calculate_sharpe_ratio(daily_rets[col], risk_free_rate=rf_rate, periods_per_year=252, window=rolling_window)
            fig_shp.add_trace(go.Scatter(
                x=roll_shp.index,
                y=roll_shp,
                name=col,
                line=dict(color=color, width=2.0),
                hovertemplate=f"<b>{col}</b>: Sharpe %{{y:.2f}}<extra></extra>",
            ))
        fig_shp.add_hline(y=0.0, line_dash="dash", line_color="#484f58")
        apply_plotly_theme(fig_shp, title=f"Rolling {rolling_window}D Sharpe Ratio", height=300)
        fig_shp.update_layout(yaxis_title="Sharpe Ratio")
        st.plotly_chart(fig_shp, use_container_width=True)

    # 3. Side-by-Side: Return Distribution (Histogram + KDE) & Risk Share Donut
    st.markdown("---")
    st.markdown("#### 🔬 Return Distribution & Portfolio Risk Share")
    col_dist, col_donut = st.columns([1.3, 1.0])

    with col_dist:
        st.markdown("##### 📊 Daily Returns Distribution (Fat Tails & Kurtosis)")
        selected_dist_asset = st.selectbox("Inspect Distribution for Asset", list(daily_rets.columns), key="sel_dist_asset")
        s_ret = daily_rets[selected_dist_asset].dropna() * 100.0
        
        # Calculate moments
        skew_val = float(stats.skew(s_ret))
        kurt_val = float(stats.kurtosis(s_ret))
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=s_ret,
            nbinsx=50,
            name="Daily Returns",
            marker_color=get_asset_color(selected_dist_asset),
            opacity=0.75,
            histnorm="probability density",
            hovertemplate="Return: %{x:.2f}%<br>Density: %{y:.3f}<extra></extra>",
        ))

        # Fitted Normal Distribution Curve
        mu, sigma = s_ret.mean(), s_ret.std()
        x_norm = np.linspace(s_ret.min(), s_ret.max(), 120)
        y_norm = stats.norm.pdf(x_norm, mu, sigma)
        fig_hist.add_trace(go.Scatter(
            x=x_norm,
            y=y_norm,
            name="Fitted Normal",
            line=dict(color="#f87171", width=2, dash="dash"),
            hovertemplate="Normal Fit: %{y:.3f}<extra></extra>",
        ))

        apply_plotly_theme(
            fig_hist,
            title=f"{selected_dist_asset} Returns (Skew: {skew_val:+.2f}, Excess Kurtosis: {kurt_val:+.2f})",
            height=320,
        )
        fig_hist.update_layout(xaxis_title="Daily Return (%)", yaxis_title="Density")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_donut:
        st.markdown("##### 🍩 Portfolio Volatility Risk Contribution")
        vol_shares = []
        labels = []
        colors = []
        for i, col in enumerate(daily_rets.columns):
            ann_vol = calculate_annualized_volatility(daily_rets[col], periods_per_year=252) * 100.0
            vol_shares.append(ann_vol)
            labels.append(col)
            colors.append(get_asset_color(col, i))

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=vol_shares,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Ann. Vol: %{value:.1f}%<br>Share: %{percent}<extra></extra>",
        )])
        apply_plotly_theme(fig_donut, title="Proportional Volatility Share", height=320)
        fig_donut.update_layout(showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    # 4. Underwater Drawdown Series
    st.markdown("---")
    st.markdown("#### 🌊 Historical Underwater Drawdown Profiles (%)")
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
    apply_plotly_theme(fig_dd, title="Peak-to-Trough Drawdown Depth from All-Time Highs", height=340)
    fig_dd.update_layout(yaxis_title="Drawdown (%)", yaxis=dict(ticksuffix="%"))
    st.plotly_chart(fig_dd, use_container_width=True)
