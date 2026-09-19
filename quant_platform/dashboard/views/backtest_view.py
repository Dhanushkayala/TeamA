"""Tab 4: Backtest Engine - Realistic Portfolio Simulation & Trade Analytics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.backtest.engine import BacktestResult
from quant_platform.backtest.metrics import calculate_performance_summary
from quant_platform.dashboard.components import apply_plotly_theme, get_asset_color, render_section_banner


def render_backtest_view(result: BacktestResult, asset_df: pd.DataFrame):
    render_section_banner(
        icon="",
        title=f"Backtest Execution: {result.strategy_name} on {result.asset_name}",
        subtitle="Simulated execution with realistic (t+1) fill lag, transaction friction, slippage, and position sizing.",
        badge_text=f"Initial: ${result.initial_capital:,.0f} • Trades: {len(result.trades)}",
        badge_color="#10b981",
    )

    # 1. Headline 8-KPI Summary Grid
    sm = result.metrics["Strategy"]
    bm = result.metrics["Benchmark"]
    
    m_cols = st.columns(4)
    with m_cols[0]:
        tot_ret = sm['Total Return (%)']
        ret_color = "#10b981" if tot_ret >= 0 else "#f43f5e"
        st.markdown(f"""
        <div class="quant-card" style="border-top: 3px solid {ret_color};">
            <div class="quant-card-title">Total Return / CAGR</div>
            <div class="quant-card-value" style="color:{ret_color};">{tot_ret:+.2f}%</div>
            <div class="quant-card-sub">CAGR: <strong style="color:var(--text-primary);">{sm['CAGR (%)']:.2f}%</strong> (Bench: {bm['Total Return (%)']:+.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    with m_cols[1]:
        shp = sm['Sharpe Ratio']
        sort = sm.get('Sortino Ratio', 0.0)
        st.markdown(f"""
        <div class="quant-card" style="border-top: 3px solid #3b82f6;">
            <div class="quant-card-title">Sharpe & Sortino</div>
            <div class="quant-card-value" style="color:#38bdf8;">{shp:.2f}</div>
            <div class="quant-card-sub">Sortino: <strong style="color:var(--text-primary);">{sort:.2f}</strong> (Bench Sharpe: {bm['Sharpe Ratio']:.2f})</div>
        </div>
        """, unsafe_allow_html=True)

    with m_cols[2]:
        mdd = sm['Max Drawdown (%)']
        calm = sm.get('Calmar Ratio', 0.0)
        mdd_color = "#f43f5e" if mdd < -20 else "#f59e0b"
        st.markdown(f"""
        <div class="quant-card" style="border-top: 3px solid {mdd_color};">
            <div class="quant-card-title">Drawdown / Calmar</div>
            <div class="quant-card-value" style="color:{mdd_color};">{mdd:.2f}%</div>
            <div class="quant-card-sub">Calmar: <strong style="color:var(--text-primary);">{calm:.2f}</strong> (Bench MDD: {bm['Max Drawdown (%)']:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    with m_cols[3]:
        wr = sm['Win Rate (%)']
        pf = sm['Profit Factor']
        st.markdown(f"""
        <div class="quant-card" style="border-top: 3px solid #8b5cf6;">
            <div class="quant-card-title">Win Rate & Trades</div>
            <div class="quant-card-value">{wr:.1f}%</div>
            <div class="quant-card-sub">{sm['Total Trades']} Trades · PF <strong style="color:#10b981;">{pf}</strong> · Fees Paid: ${sm['Total Costs Paid ($)']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Equity Curve: Strategy vs Buy & Hold Benchmark
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Portfolio Equity Growth vs Buy & Hold Benchmark ($)")
    fig_eq = go.Figure()
    
    # Strategy Equity Line
    fig_eq.add_trace(go.Scatter(
        x=result.equity_curve.index,
        y=result.equity_curve,
        name=f"Strategy: {result.strategy_name}",
        line=dict(color="#3b82f6", width=2.8),
        hovertemplate="<b>Strategy</b>: $%{y:,.2f}<extra></extra>",
    ))
    
    # Benchmark Line
    fig_eq.add_trace(go.Scatter(
        x=result.benchmark_equity.index,
        y=result.benchmark_equity,
        name=f"Benchmark: Buy & Hold {result.asset_name}",
        line=dict(color="#64748b", width=2.0, dash="dash"),
        hovertemplate="<b>Benchmark</b>: $%{y:,.2f}<extra></extra>",
    ))
    apply_plotly_theme(fig_eq, title="Capital Growth Trajectory ($100k Initial Capital)", height=380)
    fig_eq.update_layout(yaxis_title="Portfolio Value ($)", yaxis=dict(tickformat="$,.0f"))
    st.plotly_chart(fig_eq, use_container_width=True)

    # 3. Price Chart with Buy / Sell Execution Markers
    st.markdown("---")
    st.markdown("####  Trade Execution Markers on Price")
    
    fig_trades = go.Figure()
    fig_trades.add_trace(go.Scatter(
        x=asset_df.index,
        y=asset_df["close"],
        name=f"{result.asset_name} Close",
        line=dict(color="rgba(255, 255, 255, 0.4)", width=1.5),
    ))

    # Extract entry and exit points
    if result.trades:
        entries = [t for t in result.trades if t.entry_date in asset_df.index]
        exits = [t for t in result.trades if t.exit_date and t.exit_date in asset_df.index]

        if entries:
            fig_trades.add_trace(go.Scatter(
                x=[t.entry_date for t in entries],
                y=[t.entry_price for t in entries],
                mode="markers",
                name="Buy Entry (Long)",
                marker=dict(symbol="triangle-up", color="#10b981", size=11, line=dict(color="#ffffff", width=1)),
                hovertemplate="<b>BUY ENTRY</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>",
            ))
        if exits:
            fig_trades.add_trace(go.Scatter(
                x=[t.exit_date for t in exits],
                y=[t.exit_price for t in exits],
                mode="markers",
                name="Sell Exit (Flat)",
                marker=dict(symbol="triangle-down", color="#f43f5e", size=11, line=dict(color="#ffffff", width=1)),
                hovertemplate="<b>SELL EXIT</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>",
            ))

    apply_plotly_theme(fig_trades, title=f"Historical Trade Executions on {result.asset_name}", height=380)
    fig_trades.update_layout(yaxis_title="Price ($)")
    st.plotly_chart(fig_trades, use_container_width=True)

    # 4. Detailed Strategy vs Benchmark Comparison Scorecard
    st.markdown("---")
    st.markdown("####  Strategy vs Benchmark Quantitative Scorecard")
    summary_df = calculate_performance_summary(result.metrics)
    st.dataframe(summary_df, hide_index=True, use_container_width=True)

    # 5. Trade Log Table & CSV Export
    st.markdown("---")
    st.markdown("####  Executed Trade Log")
    if not result.trade_df.empty:
        st.dataframe(result.trade_df, hide_index=True, use_container_width=True)
        csv = result.trade_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=" Download Executed Trade Log (CSV)",
            data=csv,
            file_name=f"{result.asset_name}_{result.strategy_name}_trades.csv",
            mime="text/csv",
        )
    else:
        st.info("No trades were executed during this backtest timeframe.")
