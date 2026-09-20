"""Admin Dashboard View - User Management, System Diagnostics, Cache Management, and API Health."""

import os
import json
import shutil
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime

from quant_platform.dashboard.components import (
    render_section_banner,
    render_metric_card,
)
from quant_platform.auth.authenticator import _get_config, get_google_credentials
from quant_platform.auth.user_store import ACHIEVEMENTS

_USERS_DIR = Path(__file__).parents[3] / "data" / "users"
_CACHE_DIR = Path(__file__).parents[3] / ".cache"


def _get_user_profiles() -> list[dict]:
    """Load all registered user profiles from disk."""
    if not _USERS_DIR.exists():
        return []
    profiles = []
    for f in _USERS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                profiles.append(data)
        except Exception:
            pass
    return profiles


def _get_cache_stats() -> tuple[int, float]:
    """Return count of cached files and total size in MB."""
    if not _CACHE_DIR.exists():
        return 0, 0.0
    files = list(_CACHE_DIR.glob("*.*"))
    total_bytes = sum(f.stat().st_size for f in files if f.is_file())
    return len(files), total_bytes / (1024 * 1024)


def render_admin_view():
    """
    Render the comprehensive Platform Admin Dashboard.
    """
    render_section_banner(
        title="BetaScope Platform Administration & Telemetry",
        subtitle="Manage registered user accounts, inspect API gateway statuses, purge disk caches, and monitor platform health.",
        badge_text="ADMIN SECURITY & TELEMETRY",
        badge_color="#8b5cf6",
    )

    profiles = _get_user_profiles()
    cache_count, cache_mb = _get_cache_stats()

    # ── Top Metrics ──────────────────────────────────────────────────────────
    total_sessions_all = sum(p.get("total_sessions", 0) for p in profiles)
    total_achievements_unlocked = sum(len(p.get("achievements", [])) for p in profiles)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Registered Profiles",
            value=str(len(profiles)),
            subtitle=f"{total_sessions_all} Total Sessions Logged",
            color="accent",
        )
    with c2:
        render_metric_card(
            title="Disk Cache Footprint",
            value=f"{cache_mb:.2f} MB",
            subtitle=f"{cache_count} Cached Data Files",
            color="default",
        )
    with c3:
        render_metric_card(
            title="Achievements Awarded",
            value=str(total_achievements_unlocked),
            subtitle=f"Across {len(ACHIEVEMENTS)} Badge Types",
            color="positive",
        )
    with c4:
        render_metric_card(
            title="Platform Status",
            value="Operational",
            subtitle="Multi-Asset Analytics Engine",
            color="positive",
        )

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # ── Admin Tabs ───────────────────────────────────────────────────────────
    tab_users, tab_api, tab_cache = st.tabs([
        "👥 User Accounts & Audit",
        "🔑 API Gateways & AI Models",
        "🧹 Disk Cache & Storage",
    ])

    # ── TAB 1: USER ACCOUNTS ─────────────────────────────────────────────────
    with tab_users:
        st.markdown("#### Registered Trader & Analyst Profiles")
        if profiles:
            user_rows = []
            for p in profiles:
                history = p.get("session_history", [])
                best_sharpe = max([s.get("sharpe", 0.0) for s in history], default=0.0)
                user_rows.append({
                    "Username": p.get("username", "—"),
                    "Display Name": p.get("display_name", "—"),
                    "Joined": p.get("joined", "—"),
                    "Sessions": p.get("total_sessions", 0),
                    "Assets Analyzed": len(p.get("assets_analyzed", [])),
                    "Strategies Run": sum(p.get("strategies_run", {}).values()),
                    "Achievements": len(p.get("achievements", [])),
                    "Best Sharpe": f"{best_sharpe:.2f}" if best_sharpe else "—",
                })
            st.dataframe(pd.DataFrame(user_rows), use_container_width=True)
        else:
            st.info("No registered profiles yet. Run a backtest or log in with Google to create a profile.")

    # ── TAB 2: API GATEWAYS & PROVIDERS ──────────────────────────────────────
    with tab_api:
        st.markdown("#### AI Provider & Authentication Gateways")

        client_id, client_secret, redirect_uri, admin_email = get_google_credentials()
        gemini_key = _get_config("GEMINI_API_KEY", "").strip()
        openai_key = _get_config("OPENAI_API_KEY", "").strip()
        groq_key = _get_config("GROQ_API_KEY", "").strip()
        anthropic_key = _get_config("ANTHROPIC_API_KEY", "").strip()

        def _status_badge(is_set: bool) -> str:
            if is_set:
                return "✅ Configured"
            return "⚠️ Missing / Optional"

        api_data = [
            {
                "Gateway / Service": "Google OAuth2 (Login & Auth)",
                "Status": _status_badge(bool(client_id and client_secret)),
                "Details": f"Redirect: {redirect_uri or 'Not set'}",
            },
            {
                "Gateway / Service": "Google Gemini (AI Agent)",
                "Status": _status_badge(bool(gemini_key)),
                "Details": "Gemini 2.5 Flash / Pro reasoning engine",
            },
            {
                "Gateway / Service": "OpenAI (GPT-4o / GPT-4o-mini)",
                "Status": _status_badge(bool(openai_key)),
                "Details": "GPT-4o quantitative analysis",
            },
            {
                "Gateway / Service": "Groq (Llama 3.3 70B)",
                "Status": _status_badge(bool(groq_key)),
                "Details": "Ultra-low latency inference",
            },
            {
                "Gateway / Service": "Anthropic (Claude 3.5 Sonnet)",
                "Status": _status_badge(bool(anthropic_key)),
                "Details": "Claude 3.5 Sonnet reasoning",
            },
        ]
        st.table(pd.DataFrame(api_data))
        st.caption("ℹ️ Configure keys in `.env` (local) or **Streamlit Cloud App Settings → Secrets**.")

    # ── TAB 3: DISK CACHE & STORAGE ──────────────────────────────────────────
    with tab_cache:
        st.markdown("#### Market Data Cache & Disk Management")
        st.markdown(
            f"BetaScope caches downloaded Yahoo Finance market data and synthetic generators in `.cache/` to ensure ultra-fast load times and prevent API rate limits.\n\n"
            f"• **Current Cache Size**: `{cache_mb:.2f} MB`\n\n"
            f"• **Total Cached Files**: `{cache_count}`"
        )

        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            if st.button("🧹 Purge Market Data Cache", key="btn_admin_purge_cache", type="primary", use_container_width=True):
                st.cache_data.clear()
                deleted_count = 0
                if _CACHE_DIR.exists():
                    for f in _CACHE_DIR.glob("*.*"):
                        try:
                            f.unlink()
                            deleted_count += 1
                        except Exception:
                            pass
                st.success(f"Cache cleared successfully! Deleted {deleted_count} cached data files.")
                st.rerun()
