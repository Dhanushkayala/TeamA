"""Tab 3: Correlation Matrix, Rolling Dynamics, and Diversification Radar."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.indicators.returns import calculate_daily_returns
from quant_platform.analysis.correlation import (
    calculate_correlation_matrix,
    calculate_all_rolling_correlations,
)
from quant_platform.dashboard.components import apply_plotly_theme


def render_correlation_view(aligned_close: pd.DataFrame):
    st.markdown("### 🔗 Cross-Asset Correlation & Diversification")
    st.markdown("Examine static dependency matrices, diversification radar profiles, and time-varying rolling correlations.")

    daily_rets = calculate_daily_returns(aligned_close).dropna()

    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        corr_method = st.selectbox("Correlation Method", ["pearson", "spearman"], index=0)
    with ctrl_col2:
        roll_window = st.slider("Rolling Correlation Window (Days)", min_value=20, max_value=252, value=90, step=10)

    corr_mat = calculate_correlation_matrix(daily_rets, method=corr_method)

    # 1. Side-by-Side: Static Heatmap & Diversification Radar Chart
    h_col, radar_col = st.columns([1.1, 1.1])

    with h_col:
        st.markdown(f"#### 🗺️ Correlation Matrix ({corr_method.capitalize()})")
        z_vals = corr_mat.values
        x_names = list(corr_mat.columns)
        y_names = list(corr_mat.index)
        text_vals = [[f"{val:+.2f}" for val in row] for row in z_vals]

        fig_heat = go.Figure(data=go.Heatmap(
            z=z_vals,
            x=x_names,
            y=y_names,
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=14, color="#ffffff"),
            colorscale=[[0, "#ef4444"], [0.5, "#1c2333"], [1, "#3b82f6"]],
            zmin=-1.0,
            zmax=1.0,
            colorbar=dict(title="Corr", tickvals=[-1, -0.5, 0, 0.5, 1]),
        ))
        apply_plotly_theme(fig_heat, height=350)
        fig_heat.update_layout(xaxis=dict(side="bottom"))
        st.plotly_chart(fig_heat, use_container_width=True)

    with radar_col:
        st.markdown("#### 🧭 Asset Diversification Radar")
        # Build pairwise radar scores
        categories = list(corr_mat.columns)
        fig_radar = go.Figure()

        radar_colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4"]
        for idx, asset in enumerate(categories):
            # Correlation profile of `asset` with all other assets
            corrs = corr_mat.loc[asset].values.tolist()
            # Close the polygon loop
            corrs_loop = corrs + [corrs[0]]
            cat_loop = categories + [categories[0]]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=corrs_loop,
                theta=cat_loop,
                fill='toself',
                name=asset,
                line=dict(color=radar_colors[idx % len(radar_colors)], width=2),
                opacity=0.6,
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-1, 1],
                    gridcolor="#30363d",
                    linecolor="#30363d",
                    tickfont=dict(size=9, color="#7d8590"),
                ),
                angularaxis=dict(
                    gridcolor="#30363d",
                    linecolor="#30363d",
                    tickfont=dict(size=11, color="#e6edf3"),
                ),
                bgcolor="#161b22",
            ),
            paper_bgcolor="#161b22",
            font=dict(color="#e6edf3", family="Inter, sans-serif"),
            margin=dict(l=40, r=40, t=30, b=30),
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 2. Rolling Pairwise Correlation Time-Series
    st.markdown("---")
    st.markdown(f"#### 📈 Rolling {roll_window}-Day Pairwise Correlation Trends")
    rolling_pairs = calculate_all_rolling_correlations(daily_rets, window=roll_window)

    fig_roll = go.Figure()
    pair_colors = ["#38bdf8", "#fb923c", "#a855f7", "#2dd4bf", "#f43f5e", "#eab308"]
    for i, col in enumerate(rolling_pairs.columns):
        color = pair_colors[i % len(pair_colors)]
        fig_roll.add_trace(go.Scatter(
            x=rolling_pairs.index,
            y=rolling_pairs[col],
            name=col,
            line=dict(color=color, width=2.2),
            hovertemplate=f"<b>{col}</b>: %{{y:.2f}}<extra></extra>",
        ))
    fig_roll.add_hline(y=0.0, line_dash="dash", line_color="#4b5563")
    fig_roll.add_hrect(y0=-1.0, y1=-0.2, fillcolor="rgba(16, 185, 129, 0.06)", line_width=0, annotation_text="Strong Hedge Zone", annotation_position="bottom right")
    apply_plotly_theme(fig_roll, height=330)
    fig_roll.update_layout(yaxis=dict(range=[-1.05, 1.05], title="Correlation Coefficient"))
    st.plotly_chart(fig_roll, use_container_width=True)

    # 3. Dynamic Key Correlation Insights Cards
    st.markdown("---")
    st.markdown("#### 💡 Pairwise Diversification Insights")
    
    cols = list(corr_mat.columns)
    pair_list = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pair_list.append((cols[i], cols[j]))
    
    if pair_list:
        display_pairs = pair_list[:6]
        n_cols = min(len(display_pairs), 4)
        insights_cols = st.columns(n_cols)
        
        for idx, (a1, a2) in enumerate(display_pairs):
            val = corr_mat.loc[a1, a2]
            with insights_cols[idx % n_cols]:
                badge_desc = "Decoupled / Strong Hedge" if val < 0.2 else ("Moderate Co-movement" if val < 0.6 else "High Correlation")
                border_col = "#10b981" if val < 0.2 else ("#f59e0b" if val < 0.6 else "#ef4444")
                st.markdown(f"""
                <div class="quant-card" style="border-top: 3px solid {border_col};">
                    <div class="quant-card-title">{a1} vs {a2}</div>
                    <div class="quant-card-value">{val:+.2f}</div>
                    <div class="quant-card-sub">{badge_desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Select 2 or more assets to view cross-asset correlation insights.")
