"""Tab 5: Robustness Testing - Parameter Sweeps, Cost Sensitivity, Walk-Forward, and Monte Carlo."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.backtest.engine import BacktestEngine
from quant_platform.backtest.robustness import (
    run_parameter_sweep_ma,
    run_cost_sensitivity,
    run_train_test_split,
)
from quant_platform.dashboard.components import apply_plotly_theme


def render_robustness_view(asset_df: pd.DataFrame, asset_name: str, active_strategy):
    st.markdown(f"### 🛡️ Strategy Robustness & Sensitivity Suite: {asset_name}")
    st.markdown("Stress test parameters, evaluate fee friction, measure out-of-sample degradation, and simulate Monte Carlo probability envelopes.")

    rob_tab1, rob_tab2, rob_tab3, rob_tab4 = st.tabs([
        "2D Parameter Grid (Heatmap)",
        "Fee Friction Sensitivity",
        "Train / Test (In vs Out-of-Sample)",
        "🎲 Monte Carlo (500 Paths)",
    ])

    # 1. Parameter Sweep
    with rob_tab1:
        st.markdown("#### Moving Average Parameter Grid Sweep (Sharpe Ratio)")
        st.caption("Verify whether performance sits on a broad, robust plateau or is an isolated curve-fitted anomaly.")

        strat_type = "EMA" if "EMA" in active_strategy.name else "SMA"

        c_grid1, c_grid2 = st.columns([1, 2])
        with c_grid1:
            fast_windows = st.multiselect("Fast Lookback Windows", [5, 10, 15, 20, 25, 30, 40, 50], default=[5, 10, 20, 30, 50])
            slow_windows = st.multiselect("Slow Lookback Windows", [30, 50, 75, 100, 150, 200], default=[30, 50, 100, 150, 200])
            run_btn = st.button("🚀 Run Parameter Grid Sweep", key="btn_sweep")

        if run_btn or "cached_sweep" not in st.session_state:
            with st.spinner("Simulating parameter grid matrix..."):
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
                colorscale=[[0, "#ef4444"], [0.5, "#1c2333"], [1, "#10b981"]],
                colorbar=dict(title="Sharpe"),
            ))
            apply_plotly_theme(fig_grid, title=f"{strat_type} Parameter Sharpe Ratio Matrix", height=380)
            st.plotly_chart(fig_grid, use_container_width=True)

    # 2. Transaction Cost Sensitivity
    with rob_tab2:
        st.markdown("#### 📉 Transaction Fee & Slippage Friction Curve")
        st.caption("Measure how strategy profitability, CAGR, and Sharpe ratio degrade as execution fees increase from 0 to 100 bps (1.0%).")

        cost_df = run_cost_sensitivity(asset_df, active_strategy)

        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(
            x=cost_df["Cost (bps)"],
            y=cost_df["Total Return (%)"],
            name="Total Return (%)",
            line=dict(color="#3b82f6", width=2.6),
            yaxis="y1",
        ))
        fig_cost.add_trace(go.Scatter(
            x=cost_df["Cost (bps)"],
            y=cost_df["Sharpe Ratio"],
            name="Sharpe Ratio",
            line=dict(color="#10b981", width=2.6, dash="dash"),
            yaxis="y2",
        ))

        fig_cost.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            height=360,
            xaxis=dict(title="Transaction Cost (bps)", gridcolor="#30363d"),
            yaxis=dict(title="Total Return (%)", gridcolor="#30363d"),
            yaxis2=dict(title="Sharpe Ratio", overlaying="y", side="right"),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        st.dataframe(cost_df, hide_index=True, use_container_width=True)

    # 3. Train / Test Split
    with rob_tab3:
        st.markdown("#### ✂️ Chronological In-Sample vs. Out-of-Sample Validation")
        st.caption("Splits historical data chronologically to test strategy persistence and detect curve-fitting.")

        split_pct = st.slider("In-Sample (Train) Ratio (%)", min_value=50, max_value=85, value=70, step=5)
        
        tt_res = run_train_test_split(asset_df, active_strategy, train_ratio=split_pct / 100.0)

        st.info(f"Split Date: **{tt_res['split_date']}** | In-Sample: **{tt_res['train_range']}** | Out-of-Sample: **{tt_res['test_range']}**")

        tr_m = tt_res["train_metrics"]
        te_m = tt_res["test_metrics"]

        # Comparative Bar Chart: Train vs Test
        compare_metrics = ["Total Return (%)", "CAGR (%)", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown (%)", "Win Rate (%)"]
        tr_vals = [tr_m.get(m, 0.0) for m in compare_metrics]
        te_vals = [te_m.get(m, 0.0) for m in compare_metrics]

        fig_tt_bar = go.Figure()
        fig_tt_bar.add_trace(go.Bar(
            name="In-Sample (Train)",
            x=compare_metrics,
            y=tr_vals,
            marker_color="#3b82f6",
            text=[f"{v:.1f}" for v in tr_vals],
            textposition="auto",
        ))
        fig_tt_bar.add_trace(go.Bar(
            name="Out-of-Sample (Test)",
            x=compare_metrics,
            y=te_vals,
            marker_color="#10b981",
            text=[f"{v:.1f}" for v in te_vals],
            textposition="auto",
        ))
        fig_tt_bar.update_layout(barmode="group")
        apply_plotly_theme(fig_tt_bar, title="Train vs. Test Quantitative Metrics Comparison", height=320)
        st.plotly_chart(fig_tt_bar, use_container_width=True)

        c_tr, c_te = st.columns(2)
        with c_tr:
            st.markdown("##### 🟢 In-Sample (Train) Full Scorecard")
            st.dataframe(pd.DataFrame([tr_m]).T.rename(columns={0: "Value"}), use_container_width=True)
        with c_te:
            st.markdown("##### 🔵 Out-of-Sample (Test) Full Scorecard")
            st.dataframe(pd.DataFrame([te_m]).T.rename(columns={0: "Value"}), use_container_width=True)

    # 4. Monte Carlo Simulation Cone
    with rob_tab4:
        st.markdown("#### 🎲 Monte Carlo Bootstrap Simulation (500 Synthetic Paths)")
        st.caption("Reshuffles historical daily strategy returns using stationary bootstrap to generate 5th to 95th percentile forward confidence cones.")

        engine = BacktestEngine(initial_capital=100000.0)
        bt_res = engine.run(asset_df, active_strategy)
        daily_returns = bt_res.daily_returns.values
        n_bars = len(daily_returns)

        if n_bars > 10:
            num_sims = 500
            np.random.seed(42)
            # Resample returns with replacement
            resampled_returns = np.random.choice(daily_returns, size=(num_sims, n_bars), replace=True)
            equity_paths = 100000.0 * np.cumprod(1.0 + resampled_returns, axis=1)

            # Compute percentiles
            p5 = np.percentile(equity_paths, 5, axis=0)
            p25 = np.percentile(equity_paths, 25, axis=0)
            p50 = np.percentile(equity_paths, 50, axis=0)
            p75 = np.percentile(equity_paths, 75, axis=0)
            p95 = np.percentile(equity_paths, 95, axis=0)

            x_axis = bt_res.equity_curve.index

            fig_mc = go.Figure()
            # 5th - 95th percentile band
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=p95, mode="lines",
                line=dict(color="rgba(59, 130, 246, 0.2)", width=1),
                showlegend=False,
            ))
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=p5, mode="lines",
                fill="tonexty", fillcolor="rgba(59, 130, 246, 0.08)",
                line=dict(color="rgba(59, 130, 246, 0.2)", width=1),
                name="90% Confidence Interval (5th–95th)",
            ))
            # 25th - 75th percentile band
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=p75, mode="lines",
                line=dict(color="rgba(16, 185, 129, 0.3)", width=1),
                showlegend=False,
            ))
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=p25, mode="lines",
                fill="tonexty", fillcolor="rgba(16, 185, 129, 0.15)",
                line=dict(color="rgba(16, 185, 129, 0.3)", width=1),
                name="50% Confidence Interval (25th–75th)",
            ))
            # Median & Actual Strategy Path
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=p50, mode="lines",
                line=dict(color="#f59e0b", width=2.2, dash="dash"),
                name="Monte Carlo Median Path",
            ))
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=bt_res.equity_curve, mode="lines",
                line=dict(color="#ffffff", width=2.5),
                name="Actual Realized Equity Path",
            ))

            apply_plotly_theme(fig_mc, title="Monte Carlo 500-Simulation Bootstrap Confidence Envelope", height=380)
            fig_mc.update_layout(yaxis_title="Portfolio Equity ($)", yaxis=dict(tickformat="$,.0f"))
            st.plotly_chart(fig_mc, use_container_width=True)

            mc_c1, mc_c2, mc_c3 = st.columns(3)
            with mc_c1:
                st.metric("5th Percentile (Worst 5%)", f"${p5[-1]:,.2f}", delta=f"{((p5[-1]/100000.0)-1.0)*100:+.1f}%")
            with mc_c2:
                st.metric("50th Percentile (Median)", f"${p50[-1]:,.2f}", delta=f"{((p50[-1]/100000.0)-1.0)*100:+.1f}%")
            with mc_c3:
                st.metric("95th Percentile (Best 5%)", f"${p95[-1]:,.2f}", delta=f"{((p95[-1]/100000.0)-1.0)*100:+.1f}%")
