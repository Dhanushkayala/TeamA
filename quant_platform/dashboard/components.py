"""Reusable UI components, Plotly chart builders, and metric renderers."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List, Optional

from quant_platform.config import DEFAULT_ASSETS, UI_THEME

# Consistent Asset Colors — refined, no neons
ASSET_COLORS = {
    "Gold":    "#f59e0b",   # Warm amber
    "Bitcoin": "#f97316",   # Soft orange
    "NVIDIA":  "#3b82f6",   # Clear blue
}

# Fallback palette for custom tickers
_FALLBACK_PALETTE = [
    "#22c55e",  # green
    "#8b5cf6",  # purple
    "#06b6d4",  # cyan
    "#ec4899",  # rose
    "#a3e635",  # lime
    "#fb923c",  # orange-light
]


def get_asset_color(asset_name: str, fallback_idx: int = 0) -> str:
    """Return configured color for asset or fallback from palette."""
    if asset_name in ASSET_COLORS:
        return ASSET_COLORS[asset_name]
    return _FALLBACK_PALETTE[fallback_idx % len(_FALLBACK_PALETTE)]


def apply_plotly_theme(fig: go.Figure, title: Optional[str] = None, height: int = 420) -> go.Figure:
    """Apply the QuantLab dark theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=title or "",
            font=dict(size=14, color="#e6edf3", family="Plus Jakarta Sans, Inter"),
            x=0.01,
            y=0.97,
        ),
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        height=height,
        margin=dict(l=44, r=24, t=52, b=36),
        font=dict(family="Inter", color="#7d8590", size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#adbac7"),
        ),
        xaxis=dict(
            gridcolor="#21262d",
            zerolinecolor="#30363d",
            showgrid=True,
            linecolor="#30363d",
        ),
        yaxis=dict(
            gridcolor="#21262d",
            zerolinecolor="#30363d",
            showgrid=True,
            linecolor="#30363d",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1c2333",
            bordercolor="#30363d",
            font=dict(family="JetBrains Mono, monospace", size=11, color="#e6edf3"),
        ),
    )
    return fig


def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    delta: Optional[str] = None,
    delta_color: str = "normal",
    accent_color: Optional[str] = None,
) -> None:
    """Render a sleek metric card. Optionally provide accent_color for the top border."""
    delta_html = ""
    if delta:
        cls = {
            "positive": "delta-positive",
            "negative": "delta-negative",
        }.get(delta_color, "")
        arrow = "▲" if delta_color == "positive" else ("▼" if delta_color == "negative" else "")
        delta_html = f"<span class='{cls}'>{arrow} {delta}</span>"

    style_extra = f"--card-accent:{accent_color};" if accent_color else ""

    card_html = f"""
    <div class="quant-card" style="{style_extra}">
        <div class="quant-card-title">{title}</div>
        <div class="quant-card-value">{value} {delta_html}</div>
        <div class="quant-card-sub">{subtitle}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_section_header(icon: str, title: str, subtitle: str = "") -> None:
    """Render a consistent section header with icon box."""
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-icon">{icon}</div>
        <div class="section-header-text">
            <h4>{title}</h4>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer_footer() -> None:
    """Persistent disclaimer footer across all dashboard views."""
    st.markdown("""
    <div class="quant-disclaimer">
        ⚠️ <strong>Research &amp; Educational Use Only</strong> — QuantLab is for quantitative
        research, risk modeling, and historical backtesting analysis. Past performance
        does not guarantee future results. Simulated execution assumes zero liquidity
        constraints beyond modeled slippage. Not financial advice.
    </div>
    """, unsafe_allow_html=True)


# ─── Navigation Bar ──────────────────────────────────────────────────────────

# Ordered list of (key, label) for the nav
NAV_PAGES: list[tuple[str, str]] = [
    ("overview",  "🏠 Overview"),
    ("risk",      "⚡ Risk"),
    ("corr",      "🔗 Correlation"),
    ("backtest",  "⚙️ Backtest"),
    ("robust",    "🛡️ Robustness"),
    ("regimes",   "🌐 Regimes"),
    ("profile",   "👤 Profile"),
]

_NAV_STATE_KEY = "ql_active_page"


def get_active_page() -> str:
    """Return the current active page key (defaults to 'overview')."""
    return st.session_state.get(_NAV_STATE_KEY, "overview")


def render_navbar(username: str, display_name: str) -> None:
    """
    Render the sticky top navigation bar.

    Injects the logo, all nav page buttons, and a user pill on the right.
    Clicking a nav button updates session_state[_NAV_STATE_KEY] and triggers a rerun.
    """
    active = get_active_page()
    initials = "".join(w[0].upper() for w in (display_name or username).split()[:2])

    # ── HTML chrome: logo + user info (pure HTML, no interactivity) ──────────
    st.markdown(f"""
    <div class="ql-navbar">
        <div class="ql-navbar-brand">
            <div class="ql-navbar-logo">Q</div>
            <span class="ql-navbar-name">QuantLab</span>
        </div>
        <!-- nav items inserted by Streamlit columns below via CSS overlap -->
        <div style="display:flex; align-items:center; gap:10px; margin-left:auto;">
            <div style="display:flex; align-items:center; gap:8px;
                        padding:5px 12px; background:var(--bg-elevated);
                        border:1px solid var(--border); border-radius:20px;">
                <div style="width:26px; height:26px; border-radius:50%;
                            background:linear-gradient(135deg,#1d4ed8,#6366f1);
                            display:flex; align-items:center; justify-content:center;
                            font-size:0.75rem; font-weight:700; color:#fff;
                            font-family:'Plus Jakarta Sans',sans-serif;">{initials}</div>
                <span style="font-size:0.82rem; font-weight:600;
                             color:var(--text-secondary);
                             font-family:'Inter',sans-serif;">@{username}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Nav buttons rendered in a tight horizontal row ────────────────────────
    # We use columns with equal width — each column holds one button
    cols = st.columns(len(NAV_PAGES), gap="small")

    for col, (page_key, label) in zip(cols, NAV_PAGES):
        with col:
            btn_class = "ql-nav-btn-active" if active == page_key else "ql-nav-btn"
            # Wrap in a container that carries the CSS class
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state[_NAV_STATE_KEY] = page_key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

