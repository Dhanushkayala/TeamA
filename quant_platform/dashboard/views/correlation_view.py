"""Tab 3: Correlation Matrix & Rolling Inter-Asset Dynamics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from quant_platform.indicators.returns import calculate_daily_returns
from quant_platform.analysis.correlation import (
    calculate_correlation_matrix,
    calculate_all_rolling_correlations,
)
from quant_platform.dashboard.components import apply_plotly_theme


def render_correlation_view(aligned_close: pd.DataFrame):
    st.markdown("### 🔗 Cross-Asset Correlation & Diversification")
    st.markdown("Examine static dependency matrices and time-varying rolling correlations between Gold, Bitcoin, and NVIDIA.")

    daily_rets = calculate_daily_returns(aligned_close).dropna()

    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        corr_method = st.selectbox("Correlation Method", ["pearson", "spearman"], index=0)
    with ctrl_col2:
        roll_window = st.slider("Rolling Correlation Window (Days)", min_value=20, max_value=252, value=90, step=10)

    # 1. Side-by-Side: Static Heatmap & Rolling Correlation
    h_col, r_col = st.columns([1, 1.2])

    with h_col:
        st.markdown(f"#### Static Correlation Matrix ({corr_method.capitalize()})")
        corr_mat = calculate_correlation_matrix(daily_rets, method=corr_method)

        # Plotly Heatmap
        z_vals = corr_mat.values
        x_names = list(corr_mat.columns)
        y_names = list(corr_mat.index)

        # Annotations text
        text_vals = [[f"{val:.2f}" for val in row] for row in z_vals]

        fig_heat = go.Figure(data=go.Heatmap(
            z=z_vals,
            x=x_names,
            y=y_names,
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=14, color="#ffffff"),
            colorscale=[[0, "#ef4444"], [0.5, "#222634"], [1, "#2a78d6"]],
            zmin=-1.0,
            zmax=1.0,
            colorbar=dict(title="Corr", tickvals=[-1, -0.5, 0, 0.5, 1]),
        ))
        apply_plotly_theme(fig_heat, height=360)
        fig_heat.update_layout(xaxis=dict(side="bottom"))
        st.plotly_chart(fig_heat)

    with r_col:
        st.markdown(f"#### Rolling {roll_window}-Day Pairwise Correlation")
        rolling_pairs = calculate_all_rolling_correlations(daily_rets, window=roll_window)

        fig_roll = go.Figure()
        pair_colors = ["#38bdf8", "#fb923c", "#a855f7", "#2dd4bf"]
        for i, col in enumerate(rolling_pairs.columns):
            color = pair_colors[i % len(pair_colors)]
            fig_roll.add_trace(go.Scatter(
                x=rolling_pairs.index,
                y=rolling_pairs[col],
                name=col,
                line=dict(color=color, width=2.0),
            ))
        fig_roll.add_hline(y=0.0, line_dash="dash", line_color="#4b5563")
        apply_plotly_theme(fig_roll, height=360)
        fig_roll.update_layout(yaxis=dict(range=[-1.05, 1.05], title="Correlation"))
        st.plotly_chart(fig_roll)

    # 2. Key Correlation Takeaways
    st.markdown("---")
    st.markdown("#### 💡 Diversification Insights")
    
    cols = list(corr_mat.columns)
    pair_list = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pair_list.append((cols[i], cols[j]))
    
    if pair_list:
        display_pairs = pair_list[:6]  # Display up to 6 pairs in responsive columns
        n_cols = min(len(display_pairs), 4)
        insights_cols = st.columns(n_cols)
        
        for idx, (a1, a2) in enumerate(display_pairs):
            val = corr_mat.loc[a1, a2]
            with insights_cols[idx % n_cols]:
                badge_desc = "Decoupled / Strong Hedge" if val < 0.2 else ("Moderate Co-movement" if val < 0.6 else "High Correlation")
                st.markdown(f"""
                <div class="quant-card">
                    <div class="quant-card-title">{a1} vs {a2}</div>
                    <div class="quant-card-value">{val:+.2f}</div>
                    <div class="quant-card-sub">{badge_desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Select 2 or more assets to view cross-asset correlation insights.")

