"""Tab 7: AI Quantitative Research Assistant & Interactive Chatbot (App-Style Interface)."""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from quant_platform.ai.assistant import generate_quant_research_report, chat_with_quant_agent


def render_ai_view(
    asset_name: str,
    strategy_name: str,
    strategy_params: Dict[str, Any],
    backtest_metrics: Dict[str, Any],
    regime_metrics_df: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    asset_summary_metrics: Dict[str, Dict[str, Any]],
):
    # App-Style Top Header (Screenshot Design)
    st.markdown(f"""
    <div class="chat-app-header">
        <div>
            <div class="chat-app-title">
                <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg, #0d9488 0%, #2563eb 100%); display:flex; align-items:center; justify-content:center; font-size:1.1rem;"></div>
                <span>QuantAnalyst</span>
            </div>
            <div class="chat-app-subtitle">
                <span class="online-indicator"></span> Always active • Real-Time Market Intelligence
            </div>
        </div>
        <div>
            <span class="chat-context-pill"> Synced: {asset_name} ({strategy_name})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Admin settings state — hidden by default for all users
    show_settings = st.session_state.get("show_admin_llm_settings", False)

    provider_code = "auto"
    model_choice = None
    user_key = None

    # 1. Model & Provider Settings Expander (Visible ONLY when unlocked via KD@114)
    if show_settings:
        with st.expander(" LLM Provider & Model Settings (Admin Unlocked)", expanded=True):
            col_hdr1, col_hdr2 = st.columns([4, 1])
            with col_hdr1:
                st.caption(" Admin Mode Active • Type `hide` or click button to re-hide.")
            with col_hdr2:
                if st.button(" Hide Settings", key="btn_hide_llm_settings", use_container_width=True):
                    st.session_state["show_admin_llm_settings"] = False
                    st.rerun()

            c1, c2 = st.columns(2)
            with c1:
                provider = st.selectbox(
                    "LLM Provider",
                    options=[
                        "Google Gemini API",
                        "Featherless AI (Open-Source)",
                        "Anthropic (Claude)",
                        "Auto-Detect / Heuristic",
                    ],
                    index=0,
                    help="Choose Google Gemini API, Featherless AI, or Anthropic Claude to power QuantAnalyst.",
                )
            with c2:
                if "Gemini" in provider:
                    model_choice = st.selectbox(
                        "Model Architecture",
                        options=[
                            "gemini-1.5-flash",
                            "gemini-2.0-flash",
                            "gemini-1.5-pro",
                        ],
                        index=0,
                    )
                elif "Featherless" in provider:
                    model_choice = st.selectbox(
                        "Model Architecture",
                        options=[
                            "deepseek-ai/DeepSeek-V3",
                            "deepseek-ai/DeepSeek-R1",
                            "meta-llama/Meta-Llama-3.1-70B-Instruct",
                            "meta-llama/Meta-Llama-3.1-8B-Instruct",
                            "mistralai/Mistral-7B-Instruct-v0.3",
                            "Qwen/Qwen2.5-72B-Instruct",
                        ],
                        index=0,
                    )
                else:
                    model_choice = "claude-3-5-sonnet-20241022"

            if "Gemini" in provider:
                provider_code = "gemini"
                key_label = "Gemini API Key"
            elif "Featherless" in provider:
                provider_code = "featherless"
                key_label = "Featherless API Key"
            elif "Anthropic" in provider:
                provider_code = "anthropic"
                key_label = "Anthropic API Key"
            else:
                provider_code = "auto"
                key_label = "API Key"

            user_key = st.text_input(
                f"Enter {key_label} (or set in .env)",
                type="password",
                help="If left empty, automatically falls back to .env key or deterministic quantitative rule engine.",
            )

    # Prepare Context Payload
    context_payload = {
        "target_asset": asset_name,
        "active_strategy": strategy_name,
        "strategy_parameters": strategy_params,
        "strategy_metrics": backtest_metrics.get("Strategy", {}),
        "benchmark_metrics": backtest_metrics.get("Benchmark", {}),
        "regime_breakdown": regime_metrics_df.to_dict(orient="records") if not regime_metrics_df.empty else [],
        "correlation_matrix": correlation_matrix.to_dict() if not correlation_matrix.empty else {},
        "asset_macro_summary": asset_summary_metrics,
    }

    # Initialize Chat History
    if "quant_chat_messages" not in st.session_state:
        st.session_state["quant_chat_messages"] = [
            {
                "role": "assistant",
                "content": f"Hi! I am **QuantAnalyst**, your real-time quantitative assistant.\n\nI'm actively synced with your **{asset_name}** backtest (`{strategy_name}`) and cross-asset portfolio data.\n\n**Please select an analysis focus from the options below or ask me anything:**",
            }
        ]

    # Interactive Selectable Choice Chips Grid (Screenshot Style)
    st.markdown("<p style='font-size:0.82rem; color:#94a3b8; font-weight:600; margin-bottom:6px;'> QUICK SELECTION TOPICS:</p>", unsafe_allow_html=True)
    
    chip_prompt = None
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        if st.button(" Drawdown Risk", key="chip_drawdown", width="stretch"):
            chip_prompt = f"Analyze the drawdown risk, downside volatility, and capital preservation of {strategy_name} on {asset_name} relative to the benchmark."
        if st.button(" Market Regimes", key="chip_regimes", width="stretch"):
            chip_prompt = f"How did {strategy_name} perform across Bull vs Bear and Low vs High Volatility regimes on {asset_name}?"
    with c_col2:
        if st.button(" Optimize Parameters", key="chip_tune", width="stretch"):
            chip_prompt = f"Based on current backtest metrics, suggest optimal parameter tweaks and risk filters to boost the Sharpe ratio."
        if st.button(" Correlation Risks", key="chip_corr", width="stretch"):
            chip_prompt = f"Evaluate cross-asset correlation risks between {asset_name} and other assets in the portfolio."
    with c_col3:
        if st.button(" Sharpe & Volatility", key="chip_sharpe", width="stretch"):
            chip_prompt = f"Compare the risk-adjusted Sharpe, Sortino, and volatility metrics of {strategy_name} on {asset_name} vs Buy & Hold."
        if st.button(" Monte Carlo Test", key="chip_mc", width="stretch"):
            chip_prompt = f"Explain how the Monte Carlo 500-path simulation and bootstrap confidence intervals evaluate strategy robustness."
    with c_col4:
        if st.button(" Full Report", key="chip_report", width="stretch"):
            chip_prompt = f"Generate a full executive quantitative research report for {strategy_name} on {asset_name}."
        if st.button(" Risk-Managed Sizing", key="chip_sizing", width="stretch"):
            chip_prompt = f"How should I adjust position sizing or trailing stops during Bear and High Volatility regimes?"

    # Bottom Form Input Field (Screenshot Design with rounded text box & Send button)
    with st.form("quant_chat_form", clear_on_submit=True):
        f_c1, f_c2 = st.columns([5, 1])
        with f_c1:
            user_text = st.text_input(
                "Chat Input",
                placeholder="Ask or search something else about your backtest, risk metrics, or market regimes...",
                label_visibility="collapsed",
                key="input_user_query",
            )
        with f_c2:
            form_submit = st.form_submit_button("Send ", width="stretch")

    active_prompt = chip_prompt or (user_text.strip() if form_submit and user_text.strip() else None)

    if active_prompt:
        # Secret Code Check to reveal or toggle LLM Provider & Model Settings
        cleaned_cmd = active_prompt.strip()
        if cleaned_cmd == "KD@114":
            st.session_state["show_admin_llm_settings"] = True
            st.session_state["quant_chat_messages"].append({"role": "user", "content": "KD@114"})
            st.session_state["quant_chat_messages"].append({
                "role": "assistant",
                "content": " **Admin Settings Unlocked**: ` LLM Provider & Model Settings` panel is now visible above. You can configure custom LLM providers, model architectures, and API keys.",
            })
            st.rerun()
        elif cleaned_cmd.lower() in ["hide llm", "lock llm", "hide settings"] and show_settings:
            st.session_state["show_admin_llm_settings"] = False
            st.session_state["quant_chat_messages"].append({"role": "user", "content": cleaned_cmd})
            st.session_state["quant_chat_messages"].append({
                "role": "assistant",
                "content": " **Admin Settings Hidden**: ` LLM Provider & Model Settings` has been hidden.",
            })
            st.rerun()

        # Append regular user message
        st.session_state["quant_chat_messages"].append({"role": "user", "content": active_prompt})

        with st.spinner("QuantAnalyst is synthesizing live market data..."):
            ai_response = chat_with_quant_agent(
                messages=st.session_state["quant_chat_messages"],
                context_payload=context_payload,
                provider=provider_code,
                user_api_key=user_key if user_key and user_key.strip() else None,
                user_model=model_choice,
            )
            # Append assistant message
            st.session_state["quant_chat_messages"].append({"role": "assistant", "content": ai_response})


    # Chat Messages Display Area
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["quant_chat_messages"]:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])


    # Bottom Actions: Reset Chat & Direct Report
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    b_c1, b_c2 = st.columns([1, 4])
    with b_c1:
        if st.button("🧹 Clear Chat", key="btn_clear_chat", width="stretch"):
            st.session_state["quant_chat_messages"] = [
                {
                    "role": "assistant",
                    "content": f"Hi! Chat reset. Ready to evaluate **{asset_name}** (`{strategy_name}`) or answer any quantitative question!",
                }
            ]
            st.rerun()
    with b_c2:
        st.caption(" *Tip: Click any quick-action topic chip above or type your question in the search bar.*")
