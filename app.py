"""Quantitative Multi-Asset Financial Intelligence & Backtesting Platform.

Streamlit Application Entry Point.
"""

import streamlit as st
import datetime
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="BetaScope | Quantitative Multi-Asset Intelligence",
    page_icon="β",
    layout="wide",
    initial_sidebar_state="expanded",
)

from quant_platform.config import (
    DEFAULT_ASSETS,
    DEFAULT_START_DATE,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_TRANSACTION_COST_BPS,
    DEFAULT_SLIPPAGE_BPS,
    DEFAULT_RISK_FREE_RATE,
)
from quant_platform.data.fetcher import DataFetcher
from quant_platform.data.aligner import MultiAssetAligner
from quant_platform.indicators.returns import calculate_daily_returns
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
)
from quant_platform.analysis.correlation import calculate_correlation_matrix
from quant_platform.analysis.regimes import RegimeClassifier
from quant_platform.backtest.strategies import (
    SMACrossoverStrategy,
    EMATrendStrategy,
    MomentumStrategy,
    MeanReversionStrategy,
    STRATEGY_REGISTRY,
)
from quant_platform.backtest.engine import BacktestEngine
from quant_platform.auth.user_store import save_session, load_profile
from quant_platform.auth.authenticator import (
    get_auth_state,
    get_user_role,
    render_logout_button,
    get_google_credentials,
)
from quant_platform.dashboard.styles import apply_custom_css
from quant_platform.dashboard.components import (
    render_disclaimer_footer,
    render_navbar,
    get_active_page,
)
from quant_platform.dashboard.loader import get_loader_html
from quant_platform.dashboard.views import (
    render_overview_view,
    render_risk_view,
    render_correlation_view,
    render_backtest_view,
    render_robustness_view,
    render_regime_view,
    render_ai_view,
    render_profile_view,
    render_admin_view,
)


# 1. Theme State & User State
if "ql_theme" not in st.session_state:
    st.session_state["ql_theme"] = "dark"

if "username" not in st.session_state:
    st.session_state["username"] = "demo_analyst"
if "name" not in st.session_state:
    st.session_state["name"] = "Demo Analyst"
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = True

apply_custom_css(theme=st.session_state["ql_theme"])


# ─────────────────────────────────────────────────────────────────────────────
# 3. CACHED DATA LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def load_multi_asset_data(assets_list: tuple, start_date: str, end_date: str, custom_tickers_tuple: tuple):
    fetcher = DataFetcher(use_cache=True)
    raw_dfs = {}
    sources_info = {}

    for asset_name in assets_list:
        df, s_info = fetcher.fetch_asset(asset_name, start_date=start_date, end_date=end_date)
        raw_dfs[asset_name] = df
        sources_info[asset_name] = s_info

    for custom_ticker in custom_tickers_tuple:
        if custom_ticker.strip():
            c_sym = custom_ticker.strip().upper()
            df, s_info = fetcher.fetch_asset(c_sym, symbol=c_sym, start_date=start_date, end_date=end_date)
            raw_dfs[c_sym] = df
            sources_info[c_sym] = s_info

    aligned_dfs, aligned_close, fill_stats = MultiAssetAligner.align(raw_dfs, calendar_mode="equity")
    return aligned_dfs, aligned_close, fill_stats, sources_info


# ─────────────────────────────────────────────────────────────────────────────
# 3. SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px; margin-top:4px;">
        <div style="width:30px; height:30px; border-radius:8px; background:linear-gradient(135deg,#1d4ed8,#6366f1); display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff; font-size:1.05rem; box-shadow:0 2px 8px rgba(37,99,235,0.4);">&beta;</div>
        <div>
            <span style="font-size:1.05rem; font-weight:700; color:var(--text-primary); font-family:'Plus Jakarta Sans',sans-serif; letter-spacing:-0.02em;">BetaScope</span>
            <span style="font-size:0.70rem; color:var(--text-muted); display:block;">Multi-Asset Intelligence</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Theme Switcher in Sidebar as a Toggle
    def on_sidebar_theme_toggle():
        is_light = st.session_state.get("sidebar_theme_toggle", False)
        st.session_state["ql_theme"] = "light" if is_light else "dark"

    st.session_state["sidebar_theme_toggle"] = (
        st.session_state.get("ql_theme", "dark") == "light"
    )

    st.toggle(
        "Light Mode" if st.session_state.get("ql_theme", "dark") == "light" else "Dark Mode",
        key="sidebar_theme_toggle",
        on_change=on_sidebar_theme_toggle,
    )

    current_username = st.session_state.get("username", "demo_analyst")
    current_display_name = st.session_state.get("name", "Demo Analyst")
    user_prof = load_profile(current_username, current_display_name)
    user_initials = "".join(w[0].upper() for w in current_display_name.split()[:2]) or "DA"
    ach_count = len(user_prof.get("achievements", []))
    sess_count = user_prof.get("total_sessions", 0)

    st.markdown(f"""
    <div style="background:var(--card-bg, rgba(255,255,255,0.03)); border:1px solid var(--border-subtle, rgba(255,255,255,0.08)); border-radius:10px; padding:8px 10px; margin-top:8px; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:26px; height:26px; border-radius:50%; background:linear-gradient(135deg,#3b82f6,#10b981); display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:#fff;">{user_initials}</div>
            <div>
                <div style="font-size:0.80rem; font-weight:700; color:var(--text-primary);">{current_display_name}</div>
                <div style="font-size:0.68rem; color:var(--text-muted);">{sess_count} Sessions · 🏆 {ach_count} Badges</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:var(--text-muted); font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;'>Universe & Calendar</p>", unsafe_allow_html=True)

    available_defaults = list(DEFAULT_ASSETS.keys())
    selected_assets = st.multiselect(
        "Core Assets",
        options=available_defaults,
        default=["Gold", "Bitcoin", "NVIDIA"],
        label_visibility="collapsed",
    )
    st.caption("Core Assets")

    custom_ticker_input = st.text_input("Custom Tickers (e.g. SPY, TSLA)", value="", placeholder="SPY, TSLA, ETH-USD")
    custom_tickers = tuple([t.strip() for t in custom_ticker_input.split(",") if t.strip()])

    col_sd, col_ed = st.columns(2)
    with col_sd:
        start_date_val = st.date_input("Start", value=pd.to_datetime(DEFAULT_START_DATE))
    with col_ed:
        end_date_val = st.date_input("End", value=pd.to_datetime(datetime.date.today()))

    st.markdown("---")
    st.markdown("<p style='color:#7d8590; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;'>Backtesting Engine</p>", unsafe_allow_html=True)

    all_available_assets = list(selected_assets) + list(custom_tickers)
    if not all_available_assets:
        all_available_assets = ["NVIDIA"]

    target_asset = st.selectbox("Backtest Asset", all_available_assets, index=0)

    strategy_choice = st.selectbox(
        "Strategy Model",
        list(STRATEGY_REGISTRY.keys()),
        index=0,
    )

    strat_params = {}
    if strategy_choice == "SMA Crossover":
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            fast_p = st.number_input("Fast SMA", min_value=3, max_value=100, value=20, step=1)
        with c_p2:
            slow_p = st.number_input("Slow SMA", min_value=10, max_value=300, value=50, step=1)
        strategy_instance = SMACrossoverStrategy(fast_period=fast_p, slow_period=slow_p)
        strat_params = {"fast_period": fast_p, "slow_period": slow_p}

    elif strategy_choice == "EMA Trend":
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            fast_s = st.number_input("Fast EMA", min_value=3, max_value=100, value=12, step=1)
        with c_p2:
            slow_s = st.number_input("Slow EMA", min_value=10, max_value=300, value=26, step=1)
        strategy_instance = EMATrendStrategy(fast_span=fast_s, slow_span=slow_s)
        strat_params = {"fast_span": fast_s, "slow_span": slow_s}

    elif strategy_choice == "Momentum":
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            lookback = st.number_input("Lookback (Days)", min_value=5, max_value=365, value=60, step=5)
        with c_p2:
            thresh_pct = st.number_input("Threshold (%)", min_value=-20.0, max_value=50.0, value=0.0, step=0.5)
        strategy_instance = MomentumStrategy(lookback=lookback, threshold_pct=thresh_pct)
        strat_params = {"lookback": lookback, "threshold_pct": thresh_pct}

    elif strategy_choice == "Mean Reversion":
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            mr_lookback = st.number_input("Lookback", min_value=5, max_value=120, value=20, step=1)
        with c_p2:
            entry_z = st.number_input("Entry Z-Score", min_value=-4.0, max_value=-0.1, value=-1.5, step=0.1)
        exit_z = st.number_input("Exit Z-Score", min_value=-1.0, max_value=3.0, value=0.0, step=0.1)
        strategy_instance = MeanReversionStrategy(lookback=mr_lookback, entry_z=entry_z, exit_z=exit_z)
        strat_params = {"lookback": mr_lookback, "entry_z": entry_z, "exit_z": exit_z}

    st.markdown("---")
    st.markdown("<p style='color:#7d8590; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;'>Portfolio & Execution</p>", unsafe_allow_html=True)

    initial_capital = st.number_input(
        "Initial Capital ($)",
        min_value=1000.0,
        max_value=10_000_000.0,
        value=DEFAULT_INITIAL_CAPITAL,
        step=5000.0,
    )

    pos_sizing_mode = st.selectbox(
        "Position Sizing",
        ["All-In (100% Equity)", "Fixed 90%", "Fixed 75%", "Fixed 50%"],
        index=0,
    )
    sizing_fractions = {
        "All-In (100% Equity)": 1.0,
        "Fixed 90%": 0.90,
        "Fixed 75%": 0.75,
        "Fixed 50%": 0.50,
    }
    fraction_size = sizing_fractions[pos_sizing_mode]

    cost_bps = st.slider("Transaction Cost (bps)", 0, 100, int(DEFAULT_TRANSACTION_COST_BPS * 10000), step=1)
    transaction_cost_pct = cost_bps / 10000.0

    slippage_bps = st.slider("Slippage (bps)", 0, 50, int(DEFAULT_SLIPPAGE_BPS * 10000), step=1)
    slippage_pct = slippage_bps / 10000.0

    risk_free_pct = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=DEFAULT_RISK_FREE_RATE * 100.0, step=0.25)
    risk_free_rate = risk_free_pct / 100.0


# ─────────────────────────────────────────────────────────────────────────────
# 5. FETCH AND ALIGN DATA WITH GRAPHICAL LOADER
# ─────────────────────────────────────────────────────────────────────────────
if not selected_assets and not custom_tickers:
    st.error("Please select at least one asset in the sidebar.")
    st.stop()

# High-Tech Graphical Loading Screen during Multi-Asset Synchronization
loader_placeholder = st.empty()
asset_count = len(selected_assets) + len(custom_tickers)
loader_placeholder.markdown(
    get_loader_html(f"SYNCHRONIZING {asset_count} MULTI-ASSET FEEDS & CALIBRATING ENGINE..."),
    unsafe_allow_html=True,
)

aligned_dfs, aligned_close, fill_stats, sources_info = load_multi_asset_data(
    assets_list=tuple(selected_assets),
    start_date=start_date_val.strftime("%Y-%m-%d"),
    end_date=end_date_val.strftime("%Y-%m-%d"),
    custom_tickers_tuple=custom_tickers,
)

# Clear loader once synchronizing is complete
loader_placeholder.empty()

if aligned_close.empty or target_asset not in aligned_dfs:
    st.error(f"Could not load sufficient data for '{target_asset}'. Please check the date range.")
    st.stop()

target_df = aligned_dfs[target_asset]


# ─────────────────────────────────────────────────────────────────────────────
# 6. RUN BACKTEST SIMULATION
# ─────────────────────────────────────────────────────────────────────────────
engine = BacktestEngine(
    initial_capital=initial_capital,
    fraction_size=fraction_size,
    transaction_cost_pct=transaction_cost_pct,
    slippage_pct=slippage_pct,
    risk_free_rate=risk_free_rate,
    periods_per_year=252 if target_asset != "Bitcoin" else 365,
)

backtest_result = engine.run(target_df, strategy_instance, asset_name=target_asset)

# Automatically record backtest session for user profile and achievements
strat_m = backtest_result.metrics.get("Strategy", {})
save_session(
    username=st.session_state.get("username", "demo_analyst"),
    display_name=st.session_state.get("name", "Demo Analyst"),
    asset=target_asset,
    strategy=strategy_choice,
    sharpe=float(strat_m.get("Sharpe Ratio", 0.0)),
    total_return_pct=float(strat_m.get("Total Return (%)", 0.0)),
    max_drawdown_pct=float(strat_m.get("Max Drawdown (%)", 0.0)),
    assets_in_universe=list(aligned_close.columns),
)

# Precompute correlation & regimes
daily_returns_df = calculate_daily_returns(aligned_close).dropna()
corr_matrix = calculate_correlation_matrix(daily_returns_df)
classified_target = RegimeClassifier.classify(target_df, trend_sma_window=200, min_history=60)
regime_perf_df = RegimeClassifier.evaluate_regime_performance(
    classified_target,
    backtest_result.daily_returns,
    periods_per_year=252 if target_asset != "Bitcoin" else 365,
    risk_free_rate=risk_free_rate,
)

macro_summaries = {}
for a_name in aligned_close.columns:
    c_s = aligned_close[a_name]
    d_r = c_s.pct_change().dropna()
    macro_summaries[a_name] = {
        "Total Return (%)": round(((c_s.iloc[-1] / c_s.iloc[0]) - 1.0) * 100, 2),
        "Sharpe Ratio": round(calculate_sharpe_ratio(d_r, risk_free_rate=risk_free_rate, periods_per_year=252), 2),
        "Max Drawdown (%)": round(calculate_max_drawdown(c_s) * 100, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. TOP NAVIGATION BAR + PAGE ROUTING
# ─────────────────────────────────────────────────────────────────────────────
ai_nav_clicked = render_navbar()

active_page = get_active_page()

# Wrap page content in a fade-in div for smooth transitions
st.markdown('<div class="ql-page-content">', unsafe_allow_html=True)

if active_page == "overview":
    render_overview_view(
        aligned_dfs=aligned_dfs,
        aligned_close=aligned_close,
        fill_stats=fill_stats,
        risk_free_rate=risk_free_rate,
    )

elif active_page == "risk":
    render_risk_view(
        aligned_close=aligned_close,
        risk_free_rate=risk_free_rate,
    )

elif active_page == "corr":
    render_correlation_view(
        aligned_close=aligned_close,
    )

elif active_page == "backtest":
    render_backtest_view(
        result=backtest_result,
        asset_df=target_df,
    )

elif active_page == "robust":
    render_robustness_view(
        asset_df=target_df,
        asset_name=target_asset,
        active_strategy=strategy_instance,
    )

elif active_page == "regimes":
    render_regime_view(
        asset_df=target_df,
        asset_name=target_asset,
        strategy_returns=backtest_result.daily_returns,
        periods_per_year=252 if target_asset != "Bitcoin" else 365,
        risk_free_rate=risk_free_rate,
    )

elif active_page == "profile":
    render_profile_view(
        username=st.session_state.get("username", "demo_analyst"),
        display_name=st.session_state.get("name", "Demo Analyst"),
    )

elif active_page == "admin":
    render_admin_view()

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 8. AI ASSISTANT DIALOG
# ─────────────────────────────────────────────────────────────────────────────
@st.dialog("🤖 BetaScope AI — Quantitative Analyst", width="large")
def show_ai_dialog(
    asset_name: str,
    strategy_name: str,
    strategy_params: dict,
    backtest_metrics: dict,
    regime_metrics_df: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    asset_summary_metrics: dict,
    user_name: str = "Analyst",
):
    render_ai_view(
        asset_name=asset_name,
        strategy_name=strategy_name,
        strategy_params=strategy_params,
        backtest_metrics=backtest_metrics,
        regime_metrics_df=regime_metrics_df,
        correlation_matrix=correlation_matrix,
        asset_summary_metrics=asset_summary_metrics,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 9. FLOATING AI CHATBOT FAB (Bottom-Right Corner) & NAVBAR AI TRIGGER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="floating-ai-badge">
    <span class="online-indicator"></span> BetaScope AI &nbsp;·&nbsp; {target_asset}
</div>
""", unsafe_allow_html=True)

floating_clicked = st.button(
    "💬",
    key="floating_corner_ai_btn",
    help="Chat with BetaScope AI Quantitative Analyst",
)

if floating_clicked or ai_nav_clicked:
    show_ai_dialog(
        asset_name=target_asset,
        strategy_name=strategy_choice,
        strategy_params=strat_params,
        backtest_metrics=backtest_result.metrics,
        regime_metrics_df=regime_perf_df,
        correlation_matrix=corr_matrix,
        asset_summary_metrics=macro_summaries,
        user_name="Analyst",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 11. FOOTER DISCLAIMER
# ─────────────────────────────────────────────────────────────────────────────
render_disclaimer_footer()

