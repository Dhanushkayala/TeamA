"""Realistic portfolio simulation backtesting engine with strict zero look-ahead bias."""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from quant_platform.backtest.strategies import BaseStrategy
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_drawdown_series,
    calculate_max_drawdown,
    calculate_cagr,
    calculate_calmar_ratio,
)


@dataclass
class Trade:
    """Represents a completed or active trade."""
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: Optional[pd.Timestamp]
    exit_price: Optional[float]
    shares: float
    direction: str = "LONG"
    pnl: float = 0.0
    pnl_pct: float = 0.0
    holding_days: int = 0
    entry_cost: float = 0.0
    exit_cost: float = 0.0
    is_open: bool = False


@dataclass
class BacktestResult:
    """Comprehensive container for backtest simulation results."""
    asset_name: str
    strategy_name: str
    initial_capital: float
    final_equity: float
    equity_curve: pd.Series
    benchmark_equity: pd.Series
    daily_returns: pd.Series
    benchmark_returns: pd.Series
    positions: pd.Series
    signals: pd.Series
    trades: List[Trade]
    trade_df: pd.DataFrame
    total_cost_paid: float
    metrics: Dict[str, Any]


class BacktestEngine:
    """
    Simulates portfolio execution with transaction costs, slippage, and position sizing.
    
    CRITICAL LOOK-AHEAD PREVENTION:
    Signals computed at close of day t are executed at day t+1.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        position_sizing: str = "all_in",
        fraction_size: float = 1.0,
        transaction_cost_pct: float = 0.0010,
        slippage_pct: float = 0.0005,
        risk_free_rate: float = 0.04,
        periods_per_year: int = 252,
    ):
        self.initial_capital = float(initial_capital)
        self.position_sizing = position_sizing
        self.fraction_size = min(max(float(fraction_size), 0.01), 1.0)
        self.transaction_cost_pct = float(transaction_cost_pct)
        self.slippage_pct = float(slippage_pct)
        self.risk_free_rate = float(risk_free_rate)
        self.periods_per_year = int(periods_per_year)

    def run(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        asset_name: str = "Asset",
    ) -> BacktestResult:
        """
        Execute realistic backtest for a strategy on an OHLCV DataFrame.
        """
        if df.empty or len(df) < 2:
            raise ValueError(f"Insufficient data for backtest: {len(df)} bars.")

        # 1. Generate Raw Strategy Signal on Day t
        raw_signals = strategy.generate_signals(df).fillna(0.0)

        # 2. Shift signals by 1 period to prevent look-ahead bias
        # Signal at bar t close -> executable position at bar t+1
        target_positions = raw_signals.shift(1).fillna(0.0)

        n = len(df)
        dates = df.index
        closes = df["close"].values

        # Tracking state
        cash = self.initial_capital
        shares = 0.0
        equity = np.zeros(n, dtype=float)
        cash_history = np.zeros(n, dtype=float)
        shares_history = np.zeros(n, dtype=float)
        total_costs = 0.0

        trades: List[Trade] = []
        active_trade: Optional[Trade] = None

        for t in range(n):
            current_date = dates[t]
            current_price = closes[t]
            desired_pos = target_positions.iloc[t]

            # Entry Logic: desired_pos == 1 and not currently holding
            if desired_pos == 1.0 and shares == 0.0:
                exec_price = current_price * (1.0 + self.slippage_pct)
                available_capital = cash * self.fraction_size
                
                # Deduct transaction fee
                effective_capital = available_capital / (1.0 + self.transaction_cost_pct)
                shares_to_buy = effective_capital / exec_price
                cost_fee = (shares_to_buy * exec_price) * self.transaction_cost_pct

                shares = shares_to_buy
                cash -= (shares * exec_price + cost_fee)
                total_costs += cost_fee

                active_trade = Trade(
                    entry_date=current_date,
                    entry_price=exec_price,
                    exit_date=None,
                    exit_price=None,
                    shares=shares,
                    direction="LONG",
                    entry_cost=cost_fee,
                    is_open=True,
                )

            # Exit Logic: desired_pos == 0 and currently holding
            elif desired_pos == 0.0 and shares > 0.0:
                exec_price = current_price * (1.0 - self.slippage_pct)
                gross_proceeds = shares * exec_price
                cost_fee = gross_proceeds * self.transaction_cost_pct
                net_proceeds = gross_proceeds - cost_fee

                cash += net_proceeds
                total_costs += cost_fee

                if active_trade:
                    active_trade.exit_date = current_date
                    active_trade.exit_price = exec_price
                    active_trade.exit_cost = cost_fee
                    active_trade.is_open = False
                    active_trade.pnl = net_proceeds - (active_trade.shares * active_trade.entry_price + active_trade.entry_cost)
                    cost_basis = active_trade.shares * active_trade.entry_price + active_trade.entry_cost
                    active_trade.pnl_pct = (active_trade.pnl / cost_basis) if cost_basis > 0 else 0.0
                    active_trade.holding_days = (current_date - active_trade.entry_date).days
                    trades.append(active_trade)
                    active_trade = None

                shares = 0.0

            # Calculate current portfolio value
            current_portfolio_value = cash + (shares * current_price)
            equity[t] = current_portfolio_value
            cash_history[t] = cash
            shares_history[t] = shares

        # Close out active trade on final bar for accounting
        if active_trade is not None and shares > 0.0:
            final_price = closes[-1] * (1.0 - self.slippage_pct)
            gross_proceeds = shares * final_price
            cost_fee = gross_proceeds * self.transaction_cost_pct
            net_proceeds = gross_proceeds - cost_fee

            active_trade.exit_date = dates[-1]
            active_trade.exit_price = final_price
            active_trade.exit_cost = cost_fee
            active_trade.is_open = True  # Tag as marked to market
            cost_basis = active_trade.shares * active_trade.entry_price + active_trade.entry_cost
            active_trade.pnl = net_proceeds - cost_basis
            active_trade.pnl_pct = (active_trade.pnl / cost_basis) if cost_basis > 0 else 0.0
            active_trade.holding_days = (dates[-1] - active_trade.entry_date).days
            trades.append(active_trade)

        equity_series = pd.Series(equity, index=dates, name="Strategy Equity")
        strategy_daily_returns = equity_series.pct_change().fillna(0.0)

        # 3. Simulate Buy and Hold Benchmark
        bh_entry_price = closes[0] * (1.0 + self.slippage_pct)
        bh_entry_cost = self.initial_capital * self.transaction_cost_pct
        bh_shares = (self.initial_capital - bh_entry_cost) / bh_entry_price
        
        bh_equity = bh_shares * pd.Series(closes, index=dates)
        # Apply exit cost on last day
        bh_exit_cost = (bh_shares * closes[-1]) * self.transaction_cost_pct
        bh_equity.iloc[-1] = bh_equity.iloc[-1] - bh_exit_cost
        bh_equity.name = "Benchmark (Buy & Hold)"
        bh_daily_returns = bh_equity.pct_change().fillna(0.0)

        # Convert trades to DataFrame
        trade_rows = []
        for tr in trades:
            trade_rows.append({
                "Entry Date": tr.entry_date.strftime("%Y-%m-%d"),
                "Entry Price": round(tr.entry_price, 2),
                "Exit Date": tr.exit_date.strftime("%Y-%m-%d") if tr.exit_date else "Open",
                "Exit Price": round(tr.exit_price, 2) if tr.exit_price else None,
                "Shares": round(tr.shares, 4),
                "Net P&L ($)": round(tr.pnl, 2),
                "Return (%)": round(tr.pnl_pct * 100, 2),
                "Holding Days": tr.holding_days,
                "Status": "Open (M2M)" if tr.is_open else "Closed",
            })
        trade_df = pd.DataFrame(trade_rows)

        # 4. Calculate Comprehensive Metrics
        metrics = self._compute_metrics(
            equity_series=equity_series,
            strategy_daily_returns=strategy_daily_returns,
            benchmark_equity=bh_equity,
            benchmark_daily_returns=bh_daily_returns,
            trades=trades,
            total_costs=total_costs,
        )

        return BacktestResult(
            asset_name=asset_name,
            strategy_name=strategy.name,
            initial_capital=self.initial_capital,
            final_equity=float(equity_series.iloc[-1]),
            equity_curve=equity_series,
            benchmark_equity=bh_equity,
            daily_returns=strategy_daily_returns,
            benchmark_returns=bh_daily_returns,
            positions=target_positions,
            signals=raw_signals,
            trades=trades,
            trade_df=trade_df,
            total_cost_paid=round(total_costs, 2),
            metrics=metrics,
        )

    def _compute_metrics(
        self,
        equity_series: pd.Series,
        strategy_daily_returns: pd.Series,
        benchmark_equity: pd.Series,
        benchmark_daily_returns: pd.Series,
        trades: List[Trade],
        total_costs: float,
    ) -> Dict[str, Any]:
        """Compute side-by-side strategy and benchmark metrics."""
        strat_total_ret = (equity_series.iloc[-1] / self.initial_capital) - 1.0
        bench_total_ret = (benchmark_equity.iloc[-1] / self.initial_capital) - 1.0

        strat_cagr = calculate_cagr(equity_series, periods_per_year=self.periods_per_year)
        bench_cagr = calculate_cagr(benchmark_equity, periods_per_year=self.periods_per_year)

        strat_vol = calculate_annualized_volatility(strategy_daily_returns, periods_per_year=self.periods_per_year)
        bench_vol = calculate_annualized_volatility(benchmark_daily_returns, periods_per_year=self.periods_per_year)

        strat_sharpe = calculate_sharpe_ratio(
            strategy_daily_returns,
            risk_free_rate=self.risk_free_rate,
            periods_per_year=self.periods_per_year,
        )
        bench_sharpe = calculate_sharpe_ratio(
            benchmark_daily_returns,
            risk_free_rate=self.risk_free_rate,
            periods_per_year=self.periods_per_year,
        )

        strat_sortino = calculate_sortino_ratio(
            strategy_daily_returns,
            risk_free_rate=self.risk_free_rate,
            periods_per_year=self.periods_per_year,
        )
        bench_sortino = calculate_sortino_ratio(
            benchmark_daily_returns,
            risk_free_rate=self.risk_free_rate,
            periods_per_year=self.periods_per_year,
        )

        strat_mdd = calculate_max_drawdown(equity_series)
        bench_mdd = calculate_max_drawdown(benchmark_equity)

        # Calmar Ratio: CAGR / abs(Max Drawdown)
        strat_calmar = calculate_calmar_ratio(strat_cagr, strat_mdd)
        bench_calmar = calculate_calmar_ratio(bench_cagr, bench_mdd)

        # Trade metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]
        
        win_rate = (len(winning_trades) / total_trades) if total_trades > 0 else 0.0
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        if gross_loss > 0:
            profit_factor = round(gross_profit / gross_loss, 2)
        elif gross_profit > 0:
            profit_factor = 99.99  # Standard convention for 100% win rate
        else:
            profit_factor = 0.0
        
        avg_trade_pnl_pct = (np.mean([t.pnl_pct for t in trades]) * 100.0) if trades else 0.0
        avg_holding_days = (np.mean([t.holding_days for t in trades])) if trades else 0.0

        return {
            "Strategy": {
                "Total Return (%)": round(strat_total_ret * 100, 2),
                "CAGR (%)": round(strat_cagr * 100, 2),
                "Annualized Volatility (%)": round(strat_vol * 100, 2),
                "Sharpe Ratio": round(strat_sharpe, 2),
                "Sortino Ratio": round(strat_sortino if not np.isinf(strat_sortino) else 99.99, 2),
                "Max Drawdown (%)": round(strat_mdd * 100, 2),
                "Calmar Ratio": round(strat_calmar, 2),
                "Total Trades": total_trades,
                "Win Rate (%)": round(win_rate * 100, 1),
                "Profit Factor": profit_factor,
                "Avg Trade Return (%)": round(avg_trade_pnl_pct, 2),
                "Avg Holding Days": round(avg_holding_days, 1),
                "Total Costs Paid ($)": round(total_costs, 2),
            },
            "Benchmark": {
                "Total Return (%)": round(bench_total_ret * 100, 2),
                "CAGR (%)": round(bench_cagr * 100, 2),
                "Annualized Volatility (%)": round(bench_vol * 100, 2),
                "Sharpe Ratio": round(bench_sharpe, 2),
                "Sortino Ratio": round(bench_sortino if not np.isinf(bench_sortino) else 99.99, 2),
                "Max Drawdown (%)": round(bench_mdd * 100, 2),
                "Calmar Ratio": round(bench_calmar, 2),
                "Total Trades": 1,
                "Win Rate (%)": 100.0 if bench_total_ret > 0 else 0.0,
                "Profit Factor": round(max(bench_total_ret + 1.0, 0.0), 2),
                "Avg Trade Return (%)": round(bench_total_ret * 100, 2),
                "Avg Holding Days": (equity_series.index[-1] - equity_series.index[0]).days,
                "Total Costs Paid ($)": round(self.initial_capital * self.transaction_cost_pct * 2, 2),
            },
        }
