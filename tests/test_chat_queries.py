import pytest
from quant_platform.ai.assistant import chat_with_quant_agent

def test_chat_with_quant_agent_queries():
    sample_ctx = {
        'target_asset': 'Gold',
        'active_strategy': 'SMA Crossover',
        'strategy_parameters': {'fast_period': 20, 'slow_period': 50},
        'strategy_metrics': {'Total Return (%)': 190.1, 'Sharpe Ratio': 0.72, 'Max Drawdown (%)': -24.9, 'Win Rate (%)': 54.0, 'Total Trades': 32, 'Total Costs Paid ($)': 412.0, 'CAGR (%)': 15.2, 'Profit Factor': 1.65},
        'benchmark_metrics': {'Total Return (%)': 140.0, 'Sharpe Ratio': 0.55, 'Max Drawdown (%)': -32.0},
        'regime_breakdown': [{'Regime': 'Bull / Low Volatility', 'Cumulative Return (%)': 110.0, 'Sharpe Ratio': 1.2, 'Days': 600}],
        'correlation_matrix': {'Gold': {'Bitcoin': 0.15, 'NVIDIA': 0.08}},
        'asset_macro_summary': {'Gold': {'Total Return (%)': 140.0, 'Sharpe Ratio': 0.55, 'Max Drawdown (%)': -32.0}},
    }

    queries = [
        'Write a python script for rolling Sharpe ratio',
        'Explain the drawdown risk and how to stop loss',
        'How did this strategy perform in Bull vs Bear regimes?',
        'What is the difference between VaR and CVaR?',
        'Give me parameter optimization advice for SMA Crossover on Gold'
    ]

    for q in queries:
        msgs = [{'role': 'user', 'content': q}]
        res = chat_with_quant_agent(msgs, sample_ctx, provider='heuristic')
        assert len(res) > 50
        assert "Gold" in res or "Python" in res or "VaR" in res or "Sharpe" in res
