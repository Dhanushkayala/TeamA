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


def test_user_store_and_achievements():
    from quant_platform.auth.user_store import load_profile, save_session, get_recent_sessions
    test_user = "pytest_test_user"
    prof = load_profile(test_user, "Pytest User")
    assert prof["username"] == test_user

    # Save a high-sharpe session
    updated = save_session(
        username=test_user,
        display_name="Pytest User",
        asset="Bitcoin",
        strategy="Momentum",
        sharpe=2.4,
        total_return_pct=120.0,
        max_drawdown_pct=-35.0,
        assets_in_universe=["Gold", "Bitcoin", "NVIDIA"],
    )

    assert updated["total_sessions"] >= 1
    assert "first_session" in updated["achievements"]
    assert "sharpe_hunter" in updated["achievements"]
    assert "multi_asset" in updated["achievements"]
    assert "bear_survivor" in updated["achievements"]
    assert "momentum_master" in updated["achievements"]

    history = get_recent_sessions(test_user, n=5)
    assert len(history) >= 1
    assert history[0]["asset"] == "Bitcoin"

