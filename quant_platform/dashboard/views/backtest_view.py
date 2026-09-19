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
    st.markdown("Simulated portfolio execution accounting for execution lag ($t+1$), modeled transaction costs, slippage, and position sizing.")

    # 1. Headline Metric Summary Row
    sm = result.metrics["Strategy"]
    bm = result.metrics["Benchmark"]
    
    m_cols = st.columns(5)
    with m_cols[0]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Total Return</div>
            <div class="quant-card-value" style="color:{'#22c55e' if sm['Total Return (%)'] >= 0 else '#ef4444'};">{sm['Total Return (%)']:+.2f}%</div>
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
            <div class="quant-card-title">Sortino Ratio</div>
            <div class="quant-card-value">{sm.get('Sortino Ratio', 0.0):.2f}</div>
            <div class="quant-card-sub">Benchmark: {bm.get('Sortino Ratio', 0.0):.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_cols[3]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Max Drawdown</div>
            <div class="quant-card-value" style="color: {'#ef4444' if sm['Max Drawdown (%)'] < -20 else '#e6edf3'};">{sm['Max Drawdown (%)']:.2f}%</div>
            <div class="quant-card-sub">Benchmark: {bm['Max Drawdown (%)']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m_cols[4]:
        st.markdown(f"""
        <div class="quant-card">
            <div class="quant-card-title">Win Rate & Trades</div>
            <div class="quant-card-value">{sm['Win Rate (%)']:.1f}%</div>
            <div class="quant-card-sub">{sm['Total Trades']} Trades · PF {sm['Profit Factor']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 2. Side-by-Side: Equity Curve & Trade Win/Loss Donut Chart
    col_eq, col_pie = st.columns([1.3, 0.9])

    with col_eq:
        st.markdown("#### 💰 Portfolio Equity Curve vs. Benchmark ($)")
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=result.equity_curve.index,
            y=result.equity_curve,
            name=f"Strategy ({result.strategy_name})",
            line=dict(color="#3b82f6", width=2.8),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.06)',
            hovertemplate="<b>Strategy</b>: $%{y:,.2f}<extra></extra>",
        ))
        fig_eq.add_trace(go.Scatter(
            x=result.benchmark_equity.index,
            y=result.benchmark_equity,
            name="Buy & Hold Benchmark",
            line=dict(color="#64748b", width=2.0, dash="dash"),
            hovertemplate="<b>Benchmark</b>: $%{y:,.2f}<extra></extra>",
        ))
        apply_plotly_theme(fig_eq, title=f"Initial Capital: ${result.initial_capital:,.0f} → Final: ${result.final_equity:,.2f}", height=340)
        fig_eq.update_layout(yaxis_title="Portfolio Equity ($)", yaxis=dict(tickformat="$,.0f"))
        st.plotly_chart(fig_eq, use_container_width=True)

    with col_pie:
        st.markdown("#### 🎯 Trade Outcome Breakdown")
        if result.trades:
            wins = len([t for t in result.trades if t.pnl > 0])
            losses = len([t for t in result.trades if t.pnl < 0])
            breakeven = len([t for t in result.trades if t.pnl == 0])

            fig_donut = go.Figure(data=[go.Pie(
                labels=["Winning Trades", "Losing Trades", "Breakeven"],
                values=[wins, losses, breakeven],
                hole=0.55,
                marker=dict(
                    colors=["#10b981", "#ef4444", "#64748b"],
                    line=dict(color="#0d1117", width=2),
                ),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            )])
            apply_plotly_theme(fig_donut, title=f"Profit Factor: {sm['Profit Factor']}", height=340)
            fig_donut.update_layout(showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No trades executed during this backtest timeframe.")

    # 3. Chronological Trade P&L Bar Chart
    if result.trades:
        st.markdown("---")
        st.markdown("#### 📊 Individual Trade P&L (%) Timeline")
        trade_rets = [t.pnl_pct * 100.0 for t in result.trades]
        trade_dates = [t.exit_date.strftime("%Y-%m-%d") if t.exit_date else t.entry_date.strftime("%Y-%m-%d") for t in result.trades]
        trade_colors = ["#10b981" if r >= 0 else "#ef4444" for r in trade_rets]
        trade_hover = [
            f"Trade #{i+1}<br>Date: {trade_dates[i]}<br>Return: {r:+.2f}%<br>P&L: ${result.trades[i].pnl:+,.2f}<br>Hold: {result.trades[i].holding_days} days<extra></extra>"
            for i, r in enumerate(trade_rets)
        ]

        fig_pnl_bars = go.Figure()
        fig_pnl_bars.add_trace(go.Bar(
            x=[f"#{i+1}" for i in range(len(trade_rets))],
            y=trade_rets,
            marker_color=trade_colors,
            hovertemplate=trade_hover,
        ))
        fig_pnl_bars.add_hline(y=0.0, line_dash="solid", line_color="#484f58")
        apply_plotly_theme(fig_pnl_bars, title=f"Trade Returns Distribution ({len(trade_rets)} Total Trades)", height=280)
        fig_pnl_bars.update_layout(xaxis_title="Trade Number", yaxis_title="Trade Return (%)")
        st.plotly_chart(fig_pnl_bars, use_container_width=True)

    # 4. Strategy Monthly Returns Calendar Heatmap
    st.markdown("---")
    st.markdown("#### 📅 Monthly Returns Performance Matrix (%)")
    try:
        strat_monthly = (1.0 + result.daily_returns).resample("ME").prod() - 1.0
        if not strat_monthly.empty and len(strat_monthly) > 2:
            monthly_df = strat_monthly.to_frame(name="Return")
            monthly_df["Year"] = monthly_df.index.year
            monthly_df["Month"] = monthly_df.index.strftime("%b")
            month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            
            pivot_m = monthly_df.pivot(index="Year", columns="Month", values="Return")
            pivot_m = pivot_m.reindex(columns=[m for m in month_order if m in pivot_m.columns]) * 100.0
            
            z_m = pivot_m.values
            x_m = list(pivot_m.columns)
            y_m = [str(y) for y in pivot_m.index]
            text_m = [[f"{val:+.1f}%" if not np.isnan(val) else "" for val in row] for row in z_m]

            fig_monthly = go.Figure(data=go.Heatmap(
                z=z_m,
                x=x_m,
                y=y_m,
                text=text_m,
                texttemplate="%{text}",
                textfont=dict(size=12, color="#ffffff"),
                colorscale=[[0, "#ef4444"], [0.5, "#161b22"], [1, "#10b981"]],
                zmid=0.0,
                colorbar=dict(title="Monthly %"),
            ))
            apply_plotly_theme(fig_monthly, title="Historical Monthly Return Breakdown (%)", height=280)
            st.plotly_chart(fig_monthly, use_container_width=True)
    except Exception:
        pass  # Skip if insufficient data for monthly resample

    # 5. Price Chart with Buy / Sell Execution Markers
    st.markdown("---")
    st.markdown("#### 🎯 Execution Markers on Price")
    
    fig_trades = go.Figure()
    fig_trades.add_trace(go.Scatter(
        x=asset_df.index,
        y=asset_df["close"],
        name=f"{result.asset_name} Price",
        line=dict(color="#94a3b8", width=1.5),
    ))

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

    apply_plotly_theme(fig_trades, title=f"Trade Executions on {result.asset_name}", height=360)
    fig_trades.update_layout(yaxis_title="Price ($)")
    st.plotly_chart(fig_trades, use_container_width=True)

    # 6. Detailed Strategy vs Benchmark Comparison Scorecard
    st.markdown("---")
    st.markdown("#### 📋 Strategy vs. Benchmark Quantitative Scorecard")
    summary_df = calculate_performance_summary(result.metrics)
    st.dataframe(summary_df, hide_index=True, use_container_width=True)

    # 7. Trade Log Table & CSV Export
    st.markdown("---")
    st.markdown("#### 📜 Executed Trade Log")
    if not result.trade_df.empty:
        st.dataframe(result.trade_df, hide_index=True, use_container_width=True)
        csv = result.trade_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Trade Log as CSV",
            data=csv,
            file_name=f"{result.asset_name}_{result.strategy_name}_trades.csv",
            mime="text/csv",
        )
    else:
        st.info("No trades were executed during this backtest timeframe.")
