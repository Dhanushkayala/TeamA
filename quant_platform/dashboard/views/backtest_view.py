"""Tab 4: Backtest Engine - Realistic Portfolio Simulation & Trade Analytics."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from quant_platform.backtest.engine import BacktestResult
from quant_platform.backtest.metrics import calculate_performance_summary
from quant_platform.dashboard.components import apply_plotly_theme, get_asset_color


def render_backtest_view(result: BacktestResult, asset_df: pd.DataFrame):
    st.markdown(f"### ⚙️ Backtest Execution: {result.strategy_name} on {result.asset_name}")
    st.markdown("Simulated portfolio performance accounting for execution lag (t+1), transaction costs, slippage, and position sizing.")

    # 1. Headline Metric Summary Row
    sm = result.metrics["Strategy"]
    bm = result.metrics["Benchmark"]
    
    m_cols = st.columns(4)
    with m_cols[0]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Total Return</div>
            <div class="quant-card-value">{sm['Total Return (%)']:+.2f}%</div>
            <div class="quant-card-sub">Benchmark: {bm['Total Return (%)']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m_cols[1]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Sharpe Ratio</div>
            <div class="quant-card-value">{sm['Sharpe Ratio']:.2f}</div>
            <div class="quant-card-sub">Benchmark: {bm['Sharpe Ratio']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_cols[2]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Max Drawdown</div>
            <div class="quant-card-value" style="color: {'#ef4444' if sm['Max Drawdown (%)'] < -20 else '#ffffff'}">{sm['Max Drawdown (%)']:.2f}%</div>
            <div class="quant-card-sub">Benchmark: {bm['Max Drawdown (%)']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m_cols[3]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Win Rate & Trades</div>
            <div class="quant-card-value">{sm['Win Rate (%)']:.1f}%</div>
            <div class="quant-card-sub">{sm['Total Trades']} Trades · PF {sm['Profit Factor']}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Equity Curve: Strategy vs Buy & Hold Benchmark
    st.markdown("#### Portfolio Equity Curve vs Benchmark ($)")
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(
        x=result.equity_curve.index,
        y=result.equity_curve,
        name=f"Strategy ({result.strategy_name})",
        line=dict(color="#2a78d6", width=2.8),
        hovertemplate="<b>Strategy</b>: $%{y:,.2f}<extra></extra>",
    ))
    fig_eq.add_trace(go.Scatter(
        x=result.benchmark_equity.index,
        y=result.benchmark_equity,
        name="Buy & Hold Benchmark",
        line=dict(color="#64748b", width=2.0, dash="dash"),
        hovertemplate="<b>Benchmark</b>: $%{y:,.2f}<extra></extra>",
    ))
    apply_plotly_theme(fig_eq, title="Equity Growth Comparison ($100k Initial)", height=380)
    fig_eq.update_layout(yaxis_title="Portfolio Value ($)", yaxis=dict(tickformat="$,.0f"))
    st.plotly_chart(fig_eq)

    # 3. Price Chart with Buy / Sell Execution Markers
    st.markdown("---")
    st.markdown("#### 🎯 Execution Markers on Price")
    
    fig_trades = go.Figure()
    fig_trades.add_trace(go.Scatter(
        x=asset_df.index,
        y=asset_df["close"],
        name=f"{result.asset_name} Price",
        line=dict(color="#94a3b8", width=1.5),
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
                name="Buy Entry",
                marker=dict(symbol="triangle-up", color="#10b981", size=11, line=dict(color="#ffffff", width=1)),
                hovertemplate="<b>BUY</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>",
            ))
        if exits:
            fig_trades.add_trace(go.Scatter(
                x=[t.exit_date for t in exits],
                y=[t.exit_price for t in exits],
                mode="markers",
                name="Sell Exit",
                marker=dict(symbol="triangle-down", color="#ef4444", size=11, line=dict(color="#ffffff", width=1)),
                hovertemplate="<b>SELL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>",
            ))

    apply_plotly_theme(fig_trades, title=f"Trade Executions on {result.asset_name}", height=380)
    fig_trades.update_layout(yaxis_title="Price ($)")
    st.plotly_chart(fig_trades)

    # 4. Detailed Strategy vs Benchmark Comparison Table
    st.markdown("---")
    st.markdown("#### 📋 Strategy vs Benchmark Quantitative Scorecard")
    summary_df = calculate_performance_summary(result.metrics)
    st.dataframe(summary_df, hide_index=True)

    # 5. Trade Log Table & CSV Export
    st.markdown("---")
    st.markdown("#### 📜 Executed Trade Log")
    if not result.trade_df.empty:
        st.dataframe(result.trade_df, hide_index=True)
        csv = result.trade_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Trade Log as CSV",
            data=csv,
            file_name=f"{result.asset_name}_{result.strategy_name}_trades.csv",
            mime="text/csv",
        )
    else:
        st.info("No trades were executed during this backtest timeframe.")
