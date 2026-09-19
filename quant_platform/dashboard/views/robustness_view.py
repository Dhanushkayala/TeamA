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
from quant_platform.dashboard.components import apply_plotly_theme, render_section_banner, render_metric_card


def render_robustness_view(asset_df: pd.DataFrame, asset_name: str, active_strategy):
    render_section_banner(
        title=f"Strategy Robustness & Sensitivity Suite: {asset_name}",
        subtitle="Multi-dimensional parameter stability, execution cost friction curves, and in/out-of-sample degradation stress testing.",
        badge_text="STRESS TESTING ENGINE",
    )

    rob_tab1, rob_tab2, rob_tab3 = st.tabs([
        "2D Parameter Grid Sweep",
        "Transaction Cost Sensitivity",
        "Train / Test (In vs Out-of-Sample)",
    ])

    # 1. Parameter Sweep
    with rob_tab1:
        st.markdown("#### Moving Average Window Parameter Grid Sweep (Sharpe Ratio)")
        st.caption("Inspect whether strategy performance occupies a wide, stable plateau or an isolated, fragile curve-fitted spike.")

        strat_type = "EMA" if "EMA" in active_strategy.name else "SMA"

        c_grid1, c_grid2 = st.columns([1, 2])
        with c_grid1:
            fast_windows = st.multiselect("Fast Lookback Windows", [5, 10, 15, 20, 25, 30, 40, 50], default=[5, 10, 20, 30, 50])
            slow_windows = st.multiselect("Slow Lookback Windows", [30, 50, 75, 100, 150, 200], default=[30, 50, 100, 150, 200])
            run_btn = st.button("🚀 Run Parameter Grid Sweep", key="btn_sweep", use_container_width=True)

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

            # Diagnostic summary
            valid_sharpes = sharpe_mat.values[~np.isnan(sharpe_mat.values)]
            max_sharpe = float(np.nanmax(valid_sharpes)) if len(valid_sharpes) > 0 else 0.0
            mean_sharpe = float(np.nanmean(valid_sharpes)) if len(valid_sharpes) > 0 else 0.0
            pct_positive = float(np.mean(valid_sharpes > 0) * 100) if len(valid_sharpes) > 0 else 0.0

            with c_grid2:
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    render_metric_card("Peak Sharpe Ratio", f"{max_sharpe:.2f}", "Maximum grid point", color="accent")
                with mc2:
                    render_metric_card("Grid Mean Sharpe", f"{mean_sharpe:.2f}", "Mean across all windows", color="positive" if mean_sharpe > 0.5 else "default")
                with mc3:
                    render_metric_card("Profitable Combinations", f"{pct_positive:.0f}%", "Combinations with Sharpe > 0", color="positive" if pct_positive >= 70 else "warning")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            fig_grid = go.Figure(data=go.Heatmap(
                z=z_vals,
                x=x_cols,
                y=y_rows,
                text=text_matrix,
                texttemplate="%{text}",
                textfont=dict(size=12, color="#ffffff", family="JetBrains Mono, monospace"),
                colorscale=[
                    [0.0, "rgba(244, 63, 94, 0.85)"],
                    [0.4, "rgba(30, 41, 59, 0.9)"],
                    [0.7, "rgba(6, 182, 212, 0.85)"],
                    [1.0, "rgba(16, 185, 129, 0.9)"],
                ],
                colorbar=dict(
                    title=dict(text="Sharpe", font=dict(size=11, color="#94a3b8")),
                    tickfont=dict(size=10, color="#94a3b8"),
                ),
            ))
            apply_plotly_theme(fig_grid, title=f"{strat_type} Parameter Sharpe Ratio Matrix", height=400)
            st.plotly_chart(fig_grid, use_container_width=True)

    # 2. Transaction Cost Sensitivity
    with rob_tab2:
        st.markdown("#### Transaction Cost Sensitivity Curve")
        st.caption("Measure how strategy profitability and Sharpe ratio degrade as execution friction increases from 0 to 100 bps (1.0%).")

        cost_df = run_cost_sensitivity(asset_df, active_strategy)

        # Compute Breakeven Fee
        breakeven_cost = "None"
        for _, r in cost_df.iterrows():
            if r["Total Return (%)"] <= 0:
                breakeven_cost = f"{r['Cost (%)']:.2f}% ({int(r['Cost (%)']*100)} bps)"
                break

        kpi1, kpi2, kpi3 = st.columns(3)
        zero_cost_ret = cost_df.iloc[0]["Total Return (%)"] if len(cost_df) > 0 else 0
        bps10_ret = cost_df[cost_df["Cost (%)"] == 0.1]["Total Return (%)"].values
        bps10_val = bps10_ret[0] if len(bps10_ret) > 0 else (cost_df.iloc[1]["Total Return (%)"] if len(cost_df) > 1 else zero_cost_ret)

        with kpi1:
            render_metric_card("Gross Return (0 bps)", f"{zero_cost_ret:+.1f}%", "Frictionless execution", color="positive" if zero_cost_ret >= 0 else "negative")
        with kpi2:
            render_metric_card("Return at 10 bps Friction", f"{bps10_val:+.1f}%", "Institutional tier cost", color="positive" if bps10_val >= 0 else "negative")
        with kpi3:
            render_metric_card("Breakeven Cost Ceiling", breakeven_cost, "Maximum tolerable fee", color="accent" if breakeven_cost != "None" else "positive")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(
            x=cost_df["Cost (%)"],
            y=cost_df["Total Return (%)"],
            name="Total Return (%)",
            line=dict(color="#3b82f6", width=2.5),
            yaxis="y1",
        ))
        fig_cost.add_trace(go.Scatter(
            x=cost_df["Cost (%)"],
            y=cost_df["Sharpe Ratio"],
            name="Sharpe Ratio",
            line=dict(color="#10b981", width=2.5, dash="dash"),
            yaxis="y2",
        ))

        apply_plotly_theme(fig_cost, title="Transaction Friction vs Strategy Performance", height=380)
        fig_cost.update_layout(
            xaxis=dict(title="Transaction Fee (%)"),
            yaxis=dict(title="Total Return (%)"),
            yaxis2=dict(title="Sharpe Ratio", overlaying="y", side="right"),
            hovermode="x unified",
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        st.dataframe(cost_df, hide_index=True, use_container_width=True)

    # 3. Train / Test Split
    with rob_tab3:
        st.markdown("#### Chronological In-Sample vs Out-of-Sample Split")
        st.caption("Splits historical data to detect curve-fitting. High train performance with poor test performance indicates overfitting.")

        split_pct = st.slider("In-Sample (Train) Ratio (%)", min_value=50, max_value=85, value=70, step=5)
        
        tt_res = run_train_test_split(asset_df, active_strategy, train_ratio=split_pct / 100.0)

        train_sharpe = tt_res["train_metrics"].get("Sharpe Ratio", 0.0)
        test_sharpe = tt_res["test_metrics"].get("Sharpe Ratio", 0.0)
        sharpe_retention = (test_sharpe / train_sharpe * 100) if train_sharpe > 0 else 0.0

        if sharpe_retention >= 75:
            overfit_risk = ("LOW RISK", "positive", "Strategy retains strong efficiency out-of-sample")
        elif sharpe_retention >= 40:
            overfit_risk = ("MODERATE DEGRADATION", "warning", "Noticeable efficiency decay out-of-sample")
        else:
            overfit_risk = ("HIGH OVERFIT RISK", "negative", "Severe out-of-sample Sharpe collapse")

        sk1, sk2, sk3 = st.columns(3)
        with sk1:
            render_metric_card("In-Sample Sharpe", f"{train_sharpe:.2f}", f"Train: {tt_res['train_range']}", color="accent")
        with sk2:
            render_metric_card("Out-of-Sample Sharpe", f"{test_sharpe:.2f}", f"Test: {tt_res['test_range']}", color="positive" if test_sharpe > 0.5 else "warning")
        with sk3:
            render_metric_card("OOS Sharpe Retention", f"{sharpe_retention:.0f}%", overfit_risk[0], color=overfit_risk[1])

        st.markdown(f"""
        <div style="background: rgba(18, 23, 32, 0.7); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 10px 16px; margin: 12px 0; font-size: 0.84rem; color: #94a3b8;">
            📅 <strong>Split Boundary:</strong> <span style="color: #06b6d4; font-family: 'JetBrains Mono', monospace;">{tt_res['split_date']}</span> &nbsp;·&nbsp;
            <strong>Diagnostic:</strong> <span style="color: #f1f5f9;">{overfit_risk[2]}</span>
        </div>
        """, unsafe_allow_html=True)

        c_tr, c_te = st.columns(2)
        with c_tr:
            st.markdown("##### 🟢 In-Sample (Train) Metrics")
            st.dataframe(pd.DataFrame([tt_res["train_metrics"]]).T.rename(columns={0: "Value"}), use_container_width=True)
        with c_te:
            st.markdown("##### 🔵 Out-of-Sample (Test) Metrics")
            st.dataframe(pd.DataFrame([tt_res["test_metrics"]]).T.rename(columns={0: "Value"}), use_container_width=True)

