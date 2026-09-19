"""AI Quantitative Research Assistant generating data-grounded strategic commentaries."""

import os
import json
import logging
from typing import Dict, Any, Optional
import pandas as pd

from quant_platform.config import ANTHROPIC_API_KEY, FEATHERLESS_API_KEY, FEATHERLESS_MODEL, GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


def generate_quant_research_report(
    asset_name: str,
    strategy_name: str,
    strategy_params: Dict[str, Any],
    backtest_metrics: Dict[str, Any],
    regime_metrics_df: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    asset_summary_metrics: Dict[str, Dict[str, Any]],
    provider: str = "auto",  # 'gemini', 'featherless', 'anthropic', 'auto', or 'heuristic'
    user_api_key: Optional[str] = None,
    user_model: Optional[str] = None,
) -> str:
    """
    Generate an insightful, strictly data-grounded quantitative report.
    Supports Google Gemini API, Featherless AI, Anthropic API, and falls back to deterministic quant synthesis.
    """
    # Prepare structured numerical payload
    payload = {
        "target_asset": asset_name,
        "active_strategy": strategy_name,
        "strategy_parameters": strategy_params,
        "strategy_metrics": backtest_metrics.get("Strategy", {}),
        "benchmark_metrics": backtest_metrics.get("Benchmark", {}),
        "regime_breakdown": regime_metrics_df.to_dict(orient="records") if not regime_metrics_df.empty else [],
        "correlation_matrix": correlation_matrix.to_dict() if not correlation_matrix.empty else {},
        "asset_macro_summary": asset_summary_metrics,
    }

    prompt = f"""
You are an expert Senior Quantitative Analyst at a tier-1 systematic hedge fund.
Analyze the following active backtesting and multi-asset dataset:

{json.dumps(payload, indent=2)}

Write a comprehensive, professional Quantitative Research Report structured as follows:
1. **Executive Strategy Summary**: Evaluate the strategy's risk-adjusted performance (Sharpe, CAGR, Sortino/Calmar) relative to Buy & Hold.
2. **Drawdown & Risk Management Analysis**: Deep dive into capital preservation, max drawdown differences, and volatility dampening.
3. **Market Regime Breakdown**: Explain how the strategy performed across Bull vs Bear and Low vs High volatility regimes. Identify whether performance is driven by crash protection or trend riding.
4. **Cross-Asset Diversification Context**: Interpret the correlation matrix across Gold, Bitcoin, and NVIDIA.
5. **Actionable Quantitative Adjustments**: Propose specific parameter refinements or risk filters (e.g. regime-aware stops or transaction cost optimizations) strictly grounded in the numbers.

RULES:
- Ground every statement strictly in the numbers provided.
- Do NOT hallucinate returns or guarantee future outcomes.
- State clearly that historical backtest results do not guarantee future profitability.
"""

    import requests

    # 1. Try Google Gemini API if selected or auto-detected
    g_key = user_api_key if (provider == "gemini" and user_api_key) else (GEMINI_API_KEY or (user_api_key if provider == "auto" else None))
    if provider in ("gemini", "auto") and g_key:
        raw_models = [user_model, GEMINI_MODEL, "gemini-2.5-pro", "gemini-pro-latest", "gemini-3.6-flash", "gemini-flash-latest"]
        models_to_try = list(dict.fromkeys([m for m in raw_models if m]))
        for m in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={g_key}"
                headers = {"Content-Type": "application/json"}
                body = {
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 2048,
                    }
                }
                resp = requests.post(url, headers=headers, json=body, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.warning(f"Gemini API error ({m}) {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Gemini API call failed for {m}: {e}")

    # 2. Try Featherless AI if selected or auto-detected
    f_key = user_api_key if (provider == "featherless" and user_api_key) else (FEATHERLESS_API_KEY or (user_api_key if provider == "auto" else None))
    if provider in ("featherless", "auto") and f_key:
        raw_f_models = [user_model, FEATHERLESS_MODEL, "Qwen/Qwen2.5-72B-Instruct", "Qwen/Qwen2.5-7B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"]
        f_models = list(dict.fromkeys([m for m in raw_f_models if m]))
        for m in f_models:
            try:
                headers = {
                    "Authorization": f"Bearer {f_key}",
                    "Content-Type": "application/json",
                }
                body = {
                    "model": m,
                    "messages": [
                        {"role": "system", "content": "You are a professional quantitative financial researcher. Output strictly grounded, clear markdown reports."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.3,
                }
                resp = requests.post("https://api.featherless.ai/v1/chat/completions", headers=headers, json=body, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"Featherless API error ({m}) {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Featherless API call failed for {m}: {e}")

    # 3. Try Anthropic API if selected or auto-detected
    a_key = user_api_key if (provider == "anthropic" and user_api_key) else (ANTHROPIC_API_KEY or (user_api_key if provider == "auto" else None))
    if provider in ("anthropic", "auto") and a_key:
        try:
            headers = {
                "x-api-key": a_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}],
            }
            resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["content"][0]["text"]
            else:
                logger.warning(f"Anthropic API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Anthropic API call failed: {e}")

    # 4. Deterministic Rule-Based Quantitative Synthesis Fallback
    return _generate_heuristic_quant_report(payload)


def chat_with_quant_agent(
    messages: list,
    context_payload: Dict[str, Any],
    provider: str = "auto",
    user_api_key: Optional[str] = None,
    user_model: Optional[str] = None,
) -> str:
    """
    Conversational AI Chatbot interface for real-time quantitative dialogue.
    Grounded in current active backtests, regime diagnostics, and cross-asset correlations.
    """
    import requests

    target_asset = context_payload.get("target_asset", "Asset")
    strategy_name = context_payload.get("active_strategy", "Strategy")
    strat_metrics = context_payload.get("strategy_metrics", {})
    bench_metrics = context_payload.get("benchmark_metrics", {})
    regime_breakdown = context_payload.get("regime_breakdown", [])
    correlation_matrix = context_payload.get("correlation_matrix", {})
    asset_macro = context_payload.get("asset_macro_summary", {})
    robustness_data = context_payload.get("robustness_metrics", {})

    system_prompt = f"""You are QuantBot, an elite Quantitative Research Analyst & Systematic Portfolio Manager at a Tier-1 quantitative trading firm.
You have COMPLETE, comprehensive mastery of this entire quantitative intelligence and backtesting platform ('QuantLab').

=== PLATFORM ARCHITECTURE & WEBSITE CAPABILITIES ===
1. 🏠 Overview Tab: Multi-asset normalized comparisons (base-100), price action, cumulative return, volatility, Sharpe, and drawdown metrics across Gold, Bitcoin, NVIDIA, and custom tickers.
2. ⚡ Returns & Risk Tab: Rolling 30-day volatility, rolling 60-day Sharpe ratio, Value at Risk (VaR 95% & 99% parametric & historical), Conditional VaR (Expected Shortfall CVaR), and continuous Underwater Drawdown charts.
3. 🔗 Correlation Tab: Cross-asset Pearson correlation matrices and rolling 60-day pair correlations measuring asset decoupling, regime shifts, and diversification health.
4. ⚙️ Backtest Tab: Vectorized realistic execution with transaction costs (modeled in bps) and slippage friction. Strategies include SMA Crossover, EMA Trend, Momentum (ROC), and Mean Reversion (Bollinger Bands). Produces equity curves, benchmark comparisons, win rates, profit factors, and full trade ledger logs.
5. 🛡️ Robustness Tab: 500-path Monte Carlo bootstrap resampling, distribution of terminal returns, 5th-95th percentile confidence intervals, and 2D parameter sensitivity heatmaps to detect curve-fitting and overfitting.
6. 🌐 Market Regimes Tab: Multi-factor classification using 200-day SMA trend filter + 20-day ATR volatility into 4 quadrants:
   - 🟢 Bull / Low Vol: Strong trending bull markets with smooth appreciation.
   - 🟠 Bull / High Vol: High-momentum rallies with sharp whipsaws.
   - 🔵 Bear / Low Vol: Orderly downward grinds or steady bear markets.
   - 🔴 Bear / High Vol: Panic crashes, liquidity evaporation, and extreme tail risk.
7. 📁 Data Ingestion Pipeline: Real-time Alpaca API feeds + Yahoo Finance fallback + deterministic fallback, with calendar forward-fill alignment and local Parquet caching.

=== CURRENT ACTIVE WEBSITE SESSION DATA ===
- Target Asset: {target_asset}
- Active Strategy: {strategy_name} (Parameters: {context_payload.get('strategy_parameters')})
- Strategy Performance: Total Return={strat_metrics.get('Total Return (%)', 0):+.2f}%, Sharpe={strat_metrics.get('Sharpe Ratio', 0):.2f}, Max Drawdown={strat_metrics.get('Max Drawdown (%)', 0):.2f}%, Win Rate={strat_metrics.get('Win Rate (%)', 0):.1f}%, Total Trades={strat_metrics.get('Total Trades', 0)}, Costs Paid=${strat_metrics.get('Total Costs Paid ($)', 0):,.2f}
- Benchmark (Buy & Hold) Performance: Total Return={bench_metrics.get('Total Return (%)', 0):+.2f}%, Sharpe={bench_metrics.get('Sharpe Ratio', 0):.2f}, Max Drawdown={bench_metrics.get('Max Drawdown (%)', 0):.2f}%
- Market Regimes Breakdown: {json.dumps(regime_breakdown)}
- Cross-Asset Correlation Matrix: {json.dumps(correlation_matrix)}
- Multi-Asset Universe Summary: {json.dumps(asset_macro)}
- Robustness Info: {json.dumps(robustness_data)}

=== CORE INSTRUCTIONS ===
1. Provide responsive, data-grounded answers formatted in clean Markdown.
2. When asked about any feature, chart, tab, or indicator on the website, explain precisely how it works and what the active numbers mean.
3. Suggest concrete, mathematical refinements (e.g. regime-conditioned sizing, ATR trailing stops, parameter lookback expansion, fee drag reduction).
4. Maintain a sharp, professional quantitative hedge fund analyst persona.
"""

    # 1. Google Gemini API
    g_key = user_api_key if (provider == "gemini" and user_api_key) else (GEMINI_API_KEY or (user_api_key if provider == "auto" else None))
    if provider in ("gemini", "auto") and g_key:
        raw_models = [user_model, GEMINI_MODEL, "gemini-3.6-flash", "gemini-flash-latest"]
        models_to_try = list(dict.fromkeys([m for m in raw_models if m]))
        for m in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={g_key}"
                contents = []
                
                # Add system instruction as initial user/model exchange or prompt prefix
                formatted_first_user = False
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    content = msg["content"]
                    if not formatted_first_user and role == "user":
                        content = f"[SYSTEM INSTRUCTION]\n{system_prompt}\n\n[USER QUERY]\n{content}"
                        formatted_first_user = True
                    contents.append({"role": role, "parts": [{"text": content}]})

                if not contents:
                    contents = [{"role": "user", "parts": [{"text": f"{system_prompt}\n\nHello, QuantBot."}]}]

                headers = {"Content-Type": "application/json"}
                body = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 2048,
                    }
                }
                resp = requests.post(url, headers=headers, json=body, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.warning(f"Gemini Chat API error ({m}) {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Gemini Chat API call failed for {m}: {e}")

    # 2. Featherless AI
    f_key = user_api_key if (provider == "featherless" and user_api_key) else (FEATHERLESS_API_KEY or (user_api_key if provider == "auto" else None))
    if provider in ("featherless", "auto") and f_key:
        raw_f_models = [user_model, FEATHERLESS_MODEL, "Qwen/Qwen2.5-72B-Instruct", "Qwen/Qwen2.5-7B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"]
        f_models = list(dict.fromkeys([m for m in raw_f_models if m]))
        for m in f_models:
            try:
                headers = {
                    "Authorization": f"Bearer {f_key}",
                    "Content-Type": "application/json",
                }
                llm_messages = [{"role": "system", "content": system_prompt}] + messages
                body = {
                    "model": m,
                    "messages": llm_messages,
                    "max_tokens": 1500,
                    "temperature": 0.4,
                }
                resp = requests.post("https://api.featherless.ai/v1/chat/completions", headers=headers, json=body, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"Featherless Chat API error ({m}) {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Featherless Chat API call failed for {m}: {e}")

    # 3. Anthropic API
    a_key = user_api_key if (provider == "anthropic" and user_api_key) else (ANTHROPIC_API_KEY or (user_api_key if provider == "auto" else None))
    if provider in ("anthropic", "auto") and a_key:
        try:
            headers = {
                "x-api-key": a_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1500,
                "system": system_prompt,
                "messages": messages,
            }
            resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["content"][0]["text"]
            else:
                logger.warning(f"Anthropic Chat API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Anthropic Chat API failed: {e}")

    # 4. Deterministic Contextual Chatbot Fallback
    return _generate_heuristic_chat_response(messages[-1]["content"] if messages else "", context_payload)


def _generate_heuristic_chat_response(user_query: str, context_payload: Dict[str, Any]) -> str:
    """Generate comprehensive, intelligent conversational responses grounded in current session metrics."""
    q = user_query.lower()
    asset = context_payload.get("target_asset", "Asset")
    strat = context_payload.get("active_strategy", "Strategy")
    params = context_payload.get("strategy_parameters", {})
    sm = context_payload.get("strategy_metrics", {})
    bm = context_payload.get("benchmark_metrics", {})
    reg_list = context_payload.get("regime_breakdown", [])
    corr = context_payload.get("correlation_matrix", {})

    strat_ret = sm.get("Total Return (%)", 0.0)
    bench_ret = bm.get("Total Return (%)", 0.0)
    strat_sharpe = sm.get("Sharpe Ratio", 0.0)
    bench_sharpe = bm.get("Sharpe Ratio", 0.0)
    strat_mdd = sm.get("Max Drawdown (%)", 0.0)
    bench_mdd = bm.get("Max Drawdown (%)", 0.0)
    win_rate = sm.get("Win Rate (%)", 0.0)
    trades = sm.get("Total Trades", 0)
    costs = sm.get("Total Costs Paid ($)", 0.0)
    cagr = sm.get("CAGR (%)", 0.0)
    profit_factor = sm.get("Profit Factor", 1.0)

    # 1. Python Code Request
    if any(k in q for k in ["python", "code", "snippet", "script", "function", "write a", "implement"]):
        if any(k in q for k in ["sharpe", "volatility"]):
            return f"""### 💻 Python Implementation: Rolling Sharpe Ratio & Annualized Volatility

```python
import numpy as np
import pandas as pd

def calculate_rolling_sharpe(prices: pd.Series, window: int = 60, risk_free_rate: float = 0.04, periods_per_year: int = 252) -> pd.Series:
    \"\"\"Calculate rolling annualized Sharpe ratio with exact daily compound risk-free rate.\"\"\"
    daily_returns = prices.pct_change().dropna()
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_returns = daily_returns - daily_rf
    
    rolling_mean = excess_returns.rolling(window=window).mean()
    rolling_std = excess_returns.rolling(window=window).std()
    
    return (rolling_mean / rolling_std) * np.sqrt(periods_per_year)

# Usage with active {asset} asset data:
# rolling_sharpe = calculate_rolling_sharpe(df['close'], window=60)
```
- **Active {asset} Sharpe**: Current strategy annualized Sharpe is **{strat_sharpe:.2f}** vs Benchmark **{bench_sharpe:.2f}**.
"""
        elif any(k in q for k in ["drawdown", "mdd"]):
            return f"""### 💻 Python Implementation: Underwater Drawdown Series & Max Drawdown

```python
import pandas as pd

def calculate_drawdown(prices_or_equity: pd.Series) -> tuple[pd.Series, float]:
    \"\"\"Calculate underwater drawdown path and maximum drawdown percentage.\"\"\"
    cummax = prices_or_equity.cummax()
    drawdown_series = (prices_or_equity / cummax) - 1.0
    max_drawdown = drawdown_series.min()
    return drawdown_series, max_drawdown

# Example Usage:
# dd_series, mdd = calculate_drawdown(strategy_equity_curve)
# print(f"Max Peak-to-Trough Drawdown: {{mdd * 100:.2f}}%")
```
- **Active {asset} Drawdown**: Strategy MDD is **{strat_mdd:.2f}%** vs Benchmark **{bench_mdd:.2f}%**.
"""
        else:
            return f"""### 💻 Python Implementation: Vectorized {strat} Backtest

```python
import numpy as np
import pandas as pd

def run_vectorized_strategy(df: pd.DataFrame, fast: int = 20, slow: int = 50, cost_bps: float = 0.0010):
    \"\"\"Vectorized execution with 1-bar execution lag to eliminate lookahead bias.\"\"\"
    close = df['close']
    fast_ma = close.rolling(fast).mean()
    slow_ma = close.rolling(slow).mean()
    
    # Generate signal at t close, execute position at t+1
    raw_signal = (fast_ma > slow_ma).astype(float)
    position = raw_signal.shift(1).fillna(0.0)
    
    daily_returns = close.pct_change().fillna(0.0)
    trades = (position != position.shift(1)).astype(float)
    
    # Strategy returns minus fee friction
    strategy_returns = (position * daily_returns) - (trades * cost_bps)
    equity_curve = (1.0 + strategy_returns).cumprod() * 100000.0
    return equity_curve

# Active setup: {strat} on {asset} ({trades} trades, ${costs:,.2f} friction)
```
"""

    # 2. Risk & Drawdown Diagnostics
    elif any(k in q for k in ["drawdown", "risk", "loss", "mdd", "protect", "stop loss"]):
        mdd_delta = abs(bench_mdd) - abs(strat_mdd)
        return f"""### 🛡️ Risk & Drawdown Assessment for **{asset}**
- **Strategy Max Drawdown**: **{strat_mdd:.2f}%** (Benchmark: **{bench_mdd:.2f}%**).
- **Drawdown Reduction**: **{mdd_delta:+.2f}%** capital preservation improvement.
- **Profit Factor**: **{profit_factor:.2f}** over **{trades}** trades.
- **Execution Friction**: **${costs:,.2f}** total slippage & transaction costs paid.

#### 🎯 Actionable Risk Refinements:
1. **Volatility-Adjusted Stop Loss**: Place a 2.5x ATR trailing stop to exit positions dynamically when downside volatility expands.
2. **Regime Position Sizing**: Reduce allocation by 50% during *Bear / High Volatility* market states.
3. **Underwater Recovery**: With a **{win_rate:.1f}%** win rate, maintaining positive risk-to-reward ratio (skew) ensures capital grows even during choppy regimes.
"""

    # 3. Market Regimes
    elif any(k in q for k in ["regime", "bull", "bear", "volatility", "market condition", "quadrant"]):
        reg_lines = []
        for r in reg_list:
            r_name = r.get("Regime", "Unknown")
            r_ret = r.get("Cumulative Return (%)", 0.0)
            r_sh = r.get("Sharpe Ratio", 0.0)
            r_d = r.get("Days", 0)
            reg_lines.append(f"- **{r_name}** ({r_d} bars): Return **{r_ret:+.2f}%** | Sharpe **{r_sh:.2f}**")
        breakdown_text = "\n".join(reg_lines) if reg_lines else "Insufficient regime bars detected."

        return f"""### 🌪️ Market Regime Diagnostics ({asset})
We classify market states into 4 quadrants using 200-day trend SMA + 20-day ATR volatility (expanding quantiles without future leakage):
{breakdown_text}

#### 💡 Regime Takeaways:
- **Bull / Low Volatility**: Ideal trending environment where trend-following models compound steadily.
- **Bear / High Volatility**: Panic crash periods where staying in cash or hedging preserves portfolio equity.
- **Strategy Adaptation**: {strat} achieved an overall Sharpe of **{strat_sharpe:.2f}** by navigating these regime shifts.
"""

    # 4. Correlation & Diversification
    elif any(k in q for k in ["correlation", "diversif", "gold", "bitcoin", "nvda", "portfolio", "cross-asset"]):
        corr_pairs = []
        if corr:
            for a1, d in corr.items():
                if isinstance(d, dict):
                    for a2, v in d.items():
                        if a1 < a2:
                            corr_pairs.append(f"- **{a1} & {a2}**: Pearson Correlation = **{v:.2f}**")
        corr_str = "\n".join(corr_pairs) if corr_pairs else "No cross-asset pairs calculated."

        return f"""### 🌐 Cross-Asset Diversification Matrix
Active rolling correlations across your multi-asset universe:
{corr_str}

#### 💼 Portfolio Allocation Recommendations:
1. **Non-Correlated Hedges**: Pairing **Gold** (safe haven) with **Bitcoin** (macro monetary liquidity) and **NVIDIA** (secular AI equity growth) provides low co-movement during market shocks.
2. **Risk Parity Sizing**: Weight assets inversely to their annualized volatility to equalize risk contributions across the portfolio.
"""

    # 5. Value at Risk (VaR) & CVaR
    elif any(k in q for k in ["var", "cvar", "value at risk", "shortfall", "tail risk"]):
        return f"""### ⚡ Value at Risk (VaR) vs Conditional VaR (Expected Shortfall)

1. **Value at Risk (VaR 95% / 99%)**:
   - $\\text{{VaR}}_\\alpha = -\\text{{Quantile}}_\\alpha(R)$
   - Represents the maximum expected loss over a 1-day horizon at the 95% (or 99%) confidence level.
   
2. **Conditional Value at Risk (CVaR / Expected Shortfall)**:
   - $\\text{{CVaR}}_\\alpha = -\\mathbb{{E}}[R \\mid R \\le -\\text{{VaR}}_\\alpha]$
   - Measures the average loss when an extreme tail event beyond VaR occurs. CVaR is sub-additive and satisfies all axioms of a coherent risk measure.

- Check the **⚡ Returns & Risk** tab to view the live parametric and historical VaR distributions across all loaded assets!
"""

    # 6. Parameter Optimization & Tuning
    elif any(k in q for k in ["parameter", "tune", "tweak", "improve", "optimize", "sensitivity", "plateau"]):
        return f"""### ⚙️ Quantitative Parameter Tuning for **{strat}**
Current parameters: `{params}` on **{asset}**.

- **Active Performance**: Total Return **{strat_ret:+.2f}%**, CAGR **{cagr:.2f}%**, Sharpe **{strat_sharpe:.2f}**, MDD **{strat_mdd:.2f}%**.
- **Friction Drag**: Executed **{trades}** trades with **${costs:,.2f}** paid in modeled fees.

#### 🔧 Recommended Adjustments:
1. **Extend Lookbacks to Mitigate Whipsaws**: Lengthening parameters slightly filters out market noise, reducing turnover and preserving alpha against transaction friction.
2. **Inspect 2D Heatmaps in 🛡️ Robustness Tab**: Ensure optimal performance lies in a wide parameter plateau rather than an isolated spike (preventing curve overfitting).
3. **Volatility Multiplier**: Add an ATR entry filter so trade signals are only initiated when breakout volume exceeds baseline threshold.
"""

    # 7. Default Comprehensive Hedge-Fund Analyst Response
    else:
        return f"""### 🤖 QuantBot Analysis for **{asset}** (`{strat}`)

- **Performance vs Benchmark**:
  - **Strategy Total Return**: **{strat_ret:+.2f}%** (Benchmark: **{bench_ret:+.2f}%**)
  - **Annualized Sharpe Ratio**: **{strat_sharpe:.2f}** (Benchmark: **{bench_sharpe:.2f}**)
  - **Max Peak-to-Trough Drawdown**: **{strat_mdd:.2f}%** (Benchmark: **{bench_mdd:.2f}%**)
  - **Compounded CAGR**: **{cagr:.2f}%**
  - **Trade Execution**: **{trades}** trades with a **{win_rate:.1f}%** win rate and **{profit_factor:.2f}** profit factor. Total friction paid: **${costs:,.2f}**.

**You can ask me anything about:**
- 🛡️ *"How do I optimize parameters to improve Sharpe on Gold?"*
- ⚡ *"What is the Python code for calculating rolling Sharpe and VaR?"*
- 🌪️ *"Explain strategy performance in Bear / High Volatility regimes."*
- 🌐 *"How do cross-asset correlations improve portfolio diversification?"*
"""


def _generate_heuristic_quant_report(payload: Dict[str, Any]) -> str:
    """Generate professional rule-based quantitative synthesis from computed metrics."""
    asset = payload["target_asset"]
    strat = payload["active_strategy"]
    params = payload["strategy_parameters"]
    sm = payload["strategy_metrics"]
    bm = payload["benchmark_metrics"]
    reg_list = payload["regime_breakdown"]
    corr = payload["correlation_matrix"]

    strat_ret = sm.get("Total Return (%)", 0.0)
    bench_ret = bm.get("Total Return (%)", 0.0)
    strat_sharpe = sm.get("Sharpe Ratio", 0.0)
    bench_sharpe = bm.get("Sharpe Ratio", 0.0)
    strat_mdd = sm.get("Max Drawdown (%)", 0.0)
    bench_mdd = bm.get("Max Drawdown (%)", 0.0)
    win_rate = sm.get("Win Rate (%)", 0.0)
    trades = sm.get("Total Trades", 0)
    costs = sm.get("Total Costs Paid ($)", 0.0)

    # Comparative evaluation
    sharpe_diff = strat_sharpe - bench_sharpe
    mdd_improvement = abs(bench_mdd) - abs(strat_mdd)
    alpha_status = "outperformed" if strat_ret > bench_ret else "underperformed"
    risk_adj_status = "superior" if sharpe_diff > 0 else "inferior"

    report = f"""### 📊 Quantitative Intelligence & Strategy Assessment

#### 1. Executive Strategy Summary
The **{strat}** strategy applied to **{asset}** yielded a cumulative return of **{strat_ret:+.2f}%** with an annualized Sharpe ratio of **{strat_sharpe:.2f}**, compared to **{bench_ret:+.2f}%** (Sharpe **{bench_sharpe:.2f}**) for the Buy & Hold benchmark.
- **Risk-Adjusted Profile**: The strategy exhibited **{risk_adj_status}** risk-adjusted efficiency (Sharpe Δ: **{sharpe_diff:+.2f}**).
- **Execution Efficiency**: Executed **{trades}** trades with a **{win_rate:.1f}%** win rate, accumulating **${costs:,.2f}** in modeled friction and transaction costs.

#### 2. Risk & Drawdown Management
- **Maximum Drawdown**: Strategy experienced a peak-to-trough decline of **{strat_mdd:.2f}%** vs **{bench_mdd:.2f}%** for the underlying asset.
- **Capital Preservation**: {"The tactical rules successfully curtailed deep drawdowns, limiting downside exposure during severe corrections." if mdd_improvement > 0 else "Drawdown was comparable to or exceeded the buy-and-hold benchmark due to false breakout whipsaws."}

#### 3. Market Regime Diagnostics
"""
    if reg_list:
        for r in reg_list:
            r_name = r.get("Regime", "Unknown")
            r_ret = r.get("Cumulative Return (%)", 0.0)
            r_sharpe = r.get("Sharpe Ratio", 0.0)
            r_days = r.get("Days", 0)
            report += f"- **{r_name}** ({r_days} bars): Return **{r_ret:+.2f}%** | Sharpe **{r_sharpe:.2f}**\n"
    else:
        report += "- Insufficient regime sample periods for granular breakdown.\n"

    report += f"""
#### 4. Multi-Asset Diversification Context
Cross-asset correlation matrix insights:
"""
    if corr:
        for a1, pair_dict in corr.items():
            if isinstance(pair_dict, dict):
                for a2, val in pair_dict.items():
                    if a1 < a2:
                        report += f"- **{a1} / {a2}**: Pearson Correlation = **{val:.2f}**\n"

    report += f"""
#### 5. Actionable Quantitative Adjustments
1. **Parameter Tuning**: Given active parameters `{params}`, evaluate smoothing out whipsaws by expanding the lookback span or testing dynamic ATR-based volatility filters.
2. **Cost Drag Optimization**: Ensure turnover does not erode alpha in volatile sideways channels by testing minimum holding period constraints.
3. **Regime-Conditioned Sizing**: Consider reducing position sizing by 50% during *Bear / High Volatility* regimes to protect capital while maintaining full exposure during *Bull / Low Volatility* regimes.

> *Disclaimer: This analysis is generated for quantitative research and historical backtesting purposes only. Historical returns and metrics do not guarantee future performance.*
"""
    return report
