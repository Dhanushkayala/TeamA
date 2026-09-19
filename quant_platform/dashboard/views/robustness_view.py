"""Tab 5: Robustness Testing - Parameter Sweeps, Cost Sensitivity, and In/Out-of-Sample Splits."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from quant_platform.backtest.robustness import (
    run_parameter_sweep_ma,
    run_cost_sensitivity,
    run_train_test_split,
)
from quant_platform.dashboard.components import apply_plotly_theme


def render_robustness_view(asset_df: pd.DataFrame, asset_name: str, active_strategy):
    st.markdown(f"### 🛡️ Strategy Robustness & Sensitivity Suite: {asset_name}")
    st.markdown("Stress test parameters, evaluate fee friction, and measure out-of-sample degradation.")

    rob_tab1, rob_tab2, rob_tab3 = st.tabs([
        "2D Parameter Sweep (Heatmap)",
        "Transaction Cost Sensitivity",
        "Train / Test (In vs Out-of-Sample)",
    ])

    # 1. Parameter Sweep
    with rob_tab1:
        st.markdown("#### Moving Average Window Parameter Grid Sweep (Sharpe Ratio)")
        st.caption("Inspect whether performance sits on a broad, robust plateau or is an isolated curve-fitted spike.")

        strat_type = "EMA" if "EMA" in active_strategy.name else "SMA"

        c_grid1, c_grid2 = st.columns([1, 2])
        with c_grid1:
            fast_windows = st.multiselect("Fast Lookback Windows", [5, 10, 15, 20, 25, 30, 40, 50], default=[5, 10, 20, 30, 50])
            slow_windows = st.multiselect("Slow Lookback Windows", [30, 50, 75, 100, 150, 200], default=[30, 50, 100, 150, 200])
            run_btn = st.button("🚀 Run Parameter Grid Sweep", key="btn_sweep")

        if run_btn or "cached_sweep" not in st.session_state:
            with st.spinner("Computing parameter grid simulations..."):
                sharpe_mat, ret_mat = run_parameter_sweep_ma(
                    asset_df,
                    strategy_type=strat_type,
                    fast_range=sorted(fast_windows),
                    slow_range=sorted(slow_windows),
                )
                st.session_state["cached_sweep"] = (sharpe_mat, ret_mat)

        if "cached_sweep" in st.session_state:
            sharpe_mat, ret_mat = st.session_state["cached_sweep"]
            
            z_vals = sharpe_mat.values
            x_cols = [f"Fast {c}" for c in sharpe_mat.columns]
            y_rows = [f"Slow {r}" for r in sharpe_mat.index]
            text_matrix = [[f"{val:.2f}" if not np.isnan(val) else "N/A" for val in row] for row in z_vals]

            fig_grid = go.Figure(data=go.Heatmap(
                z=z_vals,
                x=x_cols,
                y=y_rows,
                text=text_matrix,
                texttemplate="%{text}",
                textfont=dict(size=13, color="#ffffff"),
                colorscale=[[0, "#ef4444"], [0.5, "#1f2430"], [1, "#10b981"]],
                colorbar=dict(title="Sharpe"),
            ))
            apply_plotly_theme(fig_grid, title=f"{strat_type} Parameter Sharpe Ratio Matrix", height=380)
            st.plotly_chart(fig_grid)

    # 2. Transaction Cost Sensitivity
    with rob_tab2:
        st.markdown("#### Transaction Cost Sensitivity Curve")
        st.caption("Measure how strategy profitability and Sharpe ratio degrade as execution fees increase from 0 to 100 bps (1.0%).")

        cost_df = run_cost_sensitivity(asset_df, active_strategy)

        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(
            x=cost_df["Cost (%)"],
            y=cost_df["Total Return (%)"],
            name="Total Return (%)",
            line=dict(color="#2a78d6", width=2.5),
            yaxis="y1",
        ))
        fig_cost.add_trace(go.Scatter(
            x=cost_df["Cost (%)"],
            y=cost_df["Sharpe Ratio"],
            name="Sharpe Ratio",
            line=dict(color="#10b981", width=2.5, dash="dash"),
            yaxis="y2",
        ))

        fig_cost.update_layout(
            template="plotly_dark",
            paper_bgcolor="#141721",
            plot_bgcolor="#141721",
            height=380,
            xaxis=dict(title="Transaction Fee (%)", gridcolor="#222634"),
            yaxis=dict(title="Total Return (%)", gridcolor="#222634"),
            yaxis2=dict(title="Sharpe Ratio", overlaying="y", side="right"),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig_cost)
        st.dataframe(cost_df, hide_index=True)

    # 3. Train / Test Split
    with rob_tab3:
        st.markdown("#### Chronological In-Sample vs Out-of-Sample Split")
        st.caption("Splits historical data to detect curve-fitting. High train performance with poor test performance indicates overfitting.")

        split_pct = st.slider("In-Sample (Train) Ratio (%)", min_value=50, max_value=85, value=70, step=5)
        
        tt_res = run_train_test_split(asset_df, active_strategy, train_ratio=split_pct / 100.0)

        st.info(f"Split Date: **{tt_res['split_date']}** | In-Sample: **{tt_res['train_range']}** | Out-of-Sample: **{tt_res['test_range']}**")

        c_tr, c_te = st.columns(2)
        with c_tr:
            st.markdown("##### 🟢 In-Sample (Train) Metrics")
            st.dataframe(pd.DataFrame([tt_res["train_metrics"]]).T.rename(columns={0: "Value"}))
        with c_te:
            st.markdown("##### 🔵 Out-of-Sample (Test) Metrics")
            st.dataframe(pd.DataFrame([tt_res["test_metrics"]]).T.rename(columns={0: "Value"}))
