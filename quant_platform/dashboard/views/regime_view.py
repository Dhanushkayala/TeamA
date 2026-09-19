"""Tab 6: Market Regime Analysis - Regime Conditioning and Macro Behavior."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from quant_platform.analysis.regimes import RegimeClassifier
from quant_platform.dashboard.components import apply_plotly_theme


def render_regime_view(
    asset_df: pd.DataFrame,
    asset_name: str,
    strategy_returns: pd.Series,
    periods_per_year: int = 252,
    risk_free_rate: float = 0.04,
):
    st.markdown(f"### 🌐 Market Regime Intelligence: {asset_name}")
    st.markdown("Classifies market conditions using 200-day Trend and historical expanding ATR Volatility without look-ahead bias.")

    # 1. Regime Classifier Execution
    classified_df = RegimeClassifier.classify(
        asset_df,
        trend_sma_window=200,
        vol_atr_window=14,
        min_history=60,
    )

    regime_perf_df = RegimeClassifier.evaluate_regime_performance(
        classified_df=classified_df,
        strategy_daily_returns=strategy_returns,
        periods_per_year=periods_per_year,
        risk_free_rate=risk_free_rate,
    )

    # 2. Time-in-Regime Summary Cards
    st.markdown("#### Regime Distribution & Time Allocation")
    cards_col = st.columns(4)
    
    badge_styles = {
        "Bull / Low Volatility": ("🟢 Bull / Low Vol", "#10b981"),
        "Bull / High Volatility": ("🟡 Bull / High Vol", "#f59e0b"),
        "Bear / Low Volatility": ("🟠 Bear / Low Vol", "#eb6834"),
        "Bear / High Volatility": ("🔴 Bear / High Vol", "#ef4444"),
    }

    for idx, row in regime_perf_df.iterrows():
        reg_title, border_color = badge_styles.get(row["Regime"], (row["Regime"], "#6b7280"))
        with cards_col[idx]:
            st.markdown(f"""
            <div class="quant-card" style="border-top: 3px solid {border_color};">
                <div class="quant-card-title">{reg_title}</div>
                <div class="quant-card-value">{row['Time in Regime (%)']}%</div>
                <div class="quant-card-sub">{row['Days']} Days · Sharpe {row['Sharpe Ratio']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    # 3. Price Chart with Regime Shading Bands
    st.markdown("---")
    st.markdown("#### 🎨 Asset Price Path Conditioned on Market Regimes")

    fig_reg = go.Figure()
    # Close price line
    fig_reg.add_trace(go.Scatter(
        x=classified_df.index,
        y=classified_df["close"],
        name=f"{asset_name} Close",
        line=dict(color="#ffffff", width=2.0),
    ))
    # 200 SMA
    if "sma_trend" in classified_df.columns:
        fig_reg.add_trace(go.Scatter(
            x=classified_df.index,
            y=classified_df["sma_trend"],
            name="200-day SMA Filter",
            line=dict(color="#94a3b8", width=1.5, dash="dash"),
        ))

    # Add background shaded regime spans
    # Group contiguous regimes to avoid creating hundreds of tiny shapes
    regime_series = classified_df["regime"]
    change_points = (regime_series != regime_series.shift(1))
    groups = change_points.cumsum()

    for _, group in classified_df.groupby(groups):
        reg = group["regime"].iloc[0]
        start_d = group.index[0]
        end_d = group.index[-1]
        color_rgba = RegimeClassifier.REGIME_COLORS.get(reg, "rgba(0,0,0,0)")

        fig_reg.add_vrect(
            x0=start_d,
            x1=end_d,
            fillcolor=color_rgba,
            layer="below",
            line_width=0,
        )

    apply_plotly_theme(fig_reg, title=f"{asset_name} Historical Regimes (Green: Bull/Low-Vol, Yellow: Bull/High-Vol, Orange: Bear/Low-Vol, Red: Bear/High-Vol)", height=400)
    fig_reg.update_layout(yaxis_title="Price ($)")
    st.plotly_chart(fig_reg)

    # 4. Regime Conditioned Performance Metrics Table & Bar Charts
    st.markdown("---")
    st.markdown("#### 📊 Strategy Performance Breakdown by Regime")
    st.dataframe(regime_perf_df, hide_index=True)

    # Bar Charts
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        fig_b1 = px.bar(
            regime_perf_df,
            x="Regime",
            y="Cumulative Return (%)",
            color="Regime",
            color_discrete_map={
                "Bull / Low Volatility": "#10b981",
                "Bull / High Volatility": "#f59e0b",
                "Bear / Low Volatility": "#eb6834",
                "Bear / High Volatility": "#ef4444",
            },
            title="Cumulative Return by Regime (%)",
        )
        apply_plotly_theme(fig_b1, height=320)
        fig_b1.update_layout(showlegend=False)
        st.plotly_chart(fig_b1)

    with b_col2:
        fig_b2 = px.bar(
            regime_perf_df,
            x="Regime",
            y="Sharpe Ratio",
            color="Regime",
            color_discrete_map={
                "Bull / Low Volatility": "#10b981",
                "Bull / High Volatility": "#f59e0b",
                "Bear / Low Volatility": "#eb6834",
                "Bear / High Volatility": "#ef4444",
            },
            title="Sharpe Ratio by Regime",
        )
        apply_plotly_theme(fig_b2, height=320)
        fig_b2.update_layout(showlegend=False)
        st.plotly_chart(fig_b2)
