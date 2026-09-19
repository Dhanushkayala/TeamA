"""Reusable UI components, Plotly chart builders, and metric renderers."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List, Optional

from quant_platform.config import DEFAULT_ASSETS, UI_THEME

# Consistent Asset Colors — modern, institutional
ASSET_COLORS = {
    "Gold":    "#f59e0b",   # Warm amber
    "Bitcoin": "#f97316",   # Vibrant orange
    "NVIDIA":  "#3b82f6",   # Deep blue
}

# Fallback palette for custom tickers
_FALLBACK_PALETTE = [
    "#10b981",  # emerald
    "#06b6d4",  # cyan
    "#8b5cf6",  # purple
    "#f43f5e",  # rose
    "#eab308",  # yellow
    "#38bdf8",  # sky blue
]


def get_asset_color(asset_name: str, fallback_idx: int = 0) -> str:
    """Return configured color for asset or fallback from palette."""
    if asset_name in ASSET_COLORS:
        return ASSET_COLORS[asset_name]
    return _FALLBACK_PALETTE[fallback_idx % len(_FALLBACK_PALETTE)]


def get_current_theme() -> str:
    """Return the active UI theme ('dark' or 'light')."""
    return st.session_state.get("ql_theme", "dark")


def apply_plotly_theme(fig: go.Figure, title: Optional[str] = None, height: int = 400, theme: Optional[str] = None) -> go.Figure:
    """Apply high-end institutional theme (Dark or Light) to any Plotly figure."""
    active_theme = theme or get_current_theme()

    if active_theme == "light":
        fig.update_layout(
            template="plotly_white",
            title=dict(
                text=title or "",
                font=dict(size=13, color="#0f172a", family="Plus Jakarta Sans, sans-serif"),
                x=0.01,
                y=0.97,
            ),
            paper_bgcolor="rgba(255, 255, 255, 0.95)",
            plot_bgcolor="#ffffff",
            height=height,
            margin=dict(l=46, r=26, t=48, b=36),
            font=dict(family="Inter, sans-serif", color="#334155", size=11),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color="#334155"),
            ),
            xaxis=dict(
                gridcolor="rgba(0, 0, 0, 0.06)",
                zerolinecolor="rgba(0, 0, 0, 0.12)",
                showgrid=True,
                linecolor="rgba(0, 0, 0, 0.12)",
            ),
            yaxis=dict(
                gridcolor="rgba(0, 0, 0, 0.06)",
                zerolinecolor="rgba(0, 0, 0, 0.12)",
                showgrid=True,
                linecolor="rgba(0, 0, 0, 0.12)",
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#ffffff",
                bordercolor="#2563eb",
                font=dict(family="JetBrains Mono, monospace", size=11, color="#0f172a"),
            ),
        )
    else:
        fig.update_layout(
            template="plotly_dark",
            title=dict(
                text=title or "",
                font=dict(size=13, color="#f1f5f9", family="Plus Jakarta Sans, sans-serif"),
                x=0.01,
                y=0.97,
            ),
            paper_bgcolor="rgba(18, 23, 32, 0.65)",
            plot_bgcolor="rgba(14, 18, 26, 0.95)",
            height=height,
            margin=dict(l=46, r=26, t=48, b=36),
            font=dict(family="Inter, sans-serif", color="#94a3b8", size=11),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color="#cbd5e1"),
            ),
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.04)",
                zerolinecolor="rgba(255, 255, 255, 0.08)",
                showgrid=True,
                linecolor="rgba(255, 255, 255, 0.08)",
            ),
            yaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.04)",
                zerolinecolor="rgba(255, 255, 255, 0.08)",
                showgrid=True,
                linecolor="rgba(255, 255, 255, 0.08)",
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#18202c",
                bordercolor="#3b82f6",
                font=dict(family="JetBrains Mono, monospace", size=11, color="#ffffff"),
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
    sub_text: Optional[str] = None,
    color: Optional[str] = None,
) -> None:
    """Render a sleek metric card with subtle glassmorphic styling."""
    display_sub = sub_text if sub_text is not None else subtitle
    
    # Resolve accent color from semantic names or direct hex
    raw_color = color or accent_color
    color_map = {
        "accent": "#3b82f6",
        "positive": "#10b981",
        "negative": "#f43f5e",
        "warning": "#f59e0b",
        "default": "rgba(255, 255, 255, 0.1)",
    }
    resolved_accent = color_map.get(raw_color, raw_color)

    delta_html = ""
    if delta:
        d_color = "#10b981" if delta_color == "positive" else ("#f43f5e" if delta_color == "negative" else "#94a3b8")
        arrow = "▲" if delta_color == "positive" else ("▼" if delta_color == "negative" else "")
        delta_html = f"<span style='font-size:0.75rem; color:{d_color}; font-weight:700; margin-left:6px; background:rgba(255,255,255,0.04); padding:2px 6px; border-radius:4px;'>{arrow} {delta}</span>"

    border_style = f"border-top: 3px solid {resolved_accent};" if resolved_accent else ""

    card_html = f"""
    <div class="quant-card" style="{border_style}">
        <div class="quant-card-title">{title}</div>
        <div class="quant-card-value">{value} {delta_html}</div>
        <div class="quant-card-sub">{display_sub}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_section_banner(
    title: str,
    subtitle: str = "",
    badge_text: str = "",
    badge_color: str = "#3b82f6",
    icon: str = "",
) -> None:
    """Render an impressive section hero banner."""
    badge_html = f"<span style='font-size:0.75rem; font-weight:600; color:{badge_color}; background:rgba(255,255,255,0.06); padding:4px 10px; border-radius:12px; border:1px solid rgba(255,255,255,0.1);'>{badge_text}</span>" if badge_text else ""

    st.markdown(f"""
    <div class="section-banner">
        <div class="section-banner-left">
            <div class="section-banner-icon">{icon}</div>
            <div>
                <h3 class="section-banner-title">{title}</h3>
                <p class="section-banner-sub">{subtitle}</p>
            </div>
        </div>
        <div>
            {badge_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Backward-compatible section header wrapper."""
    render_section_banner(title=title, subtitle=subtitle, icon=icon)


def render_disclaimer_footer() -> None:
    """Persistent disclaimer footer across all dashboard views."""
    st.markdown("""
    <div class="quant-disclaimer">
        ⚠️ <strong>Research &amp; Educational System</strong> — BetaScope provides historical simulation, risk modeling, and algorithmic intelligence. Simulated execution assumes zero liquidity constraints beyond modeled slippage. Past results do not guarantee future performance.
    </div>
    """, unsafe_allow_html=True)


# ─── Navigation Bar ──────────────────────────────────────────────────────────

NAV_PAGES: list[tuple[str, str]] = [
    ("overview",  "Overview"),
    ("risk",      "Risk"),
    ("corr",      "Correlation"),
    ("backtest",  "Backtest"),
    ("robust",    "Robustness"),
    ("regimes",   "Regimes"),
]

def get_nav_pages() -> list[tuple[str, str]]:
    return NAV_PAGES.copy()

_NAV_STATE_KEY = "ql_active_page"


def get_active_page() -> str:
    """Return the current active page key (defaults to 'overview')."""
    return st.session_state.get(_NAV_STATE_KEY, "overview")


def render_navbar() -> None:
    """
    Render the unified sticky top navigation bar.
    Integrates Brand/Logo, Live sync badge, segmented page navigation,
    and Light/Dark Mode toggle switch.
    """
    active = get_active_page()
    theme = get_current_theme()

    def on_nav_theme_toggle_change():
        is_light = st.session_state.get("nav_theme_toggle_switch", False)
        st.session_state["ql_theme"] = "light" if is_light else "dark"

    # Synchronize toggle state before widget instantiation
    st.session_state["nav_theme_toggle_switch"] = (theme == "light")

    st.markdown("""
    <div style="background:var(--bg-glass); backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
                border:1px solid var(--border); border-radius:14px; padding:8px 14px; margin-bottom:14px;
                box-shadow:var(--shadow-card);">
    """, unsafe_allow_html=True)

    col_brand, col_nav, col_toggle = st.columns(
        [2.5, 6.0, 1.5],
        vertical_alignment="center",
        gap="small"
    )

    with col_brand:
        st.markdown(f"""
        <div class="ql-navbar-brand" style="display:flex; align-items:center; gap:8px;">
            <div class="ql-navbar-logo" style="width:30px; height:30px; border-radius:8px;
                        background:linear-gradient(135deg,#2563eb,#7c3aed);
                        display:flex; align-items:center; justify-content:center;
                        font-weight:800; font-size:1.05rem; color:#fff;
                        box-shadow:0 2px 8px rgba(37,99,235,0.4);">&beta;</div>
            <div>
                <span class="ql-navbar-name" style="font-size:1.05rem; font-weight:700; color:var(--text-primary);
                             font-family:'Plus Jakarta Sans',sans-serif; letter-spacing:-0.02em;">BetaScope</span>
            </div>
            <div class="ql-live-tag" style="margin-left:2px; font-size:0.68rem; padding:2px 7px;">
                <span class="ql-live-dot"></span> Active
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_nav:
        nav_pages_list = get_nav_pages()
        page_labels = [label for key, label in nav_pages_list]
        default_label = next((label for key, label in nav_pages_list if key == active), page_labels[0])
        selected_label = st.segmented_control(
            "Navigation",
            options=page_labels,
            default=default_label,
            label_visibility="collapsed",
            key="nav_bar_segmented_control",
        )
        if selected_label and selected_label != default_label:
            selected_key = next(key for key, label in nav_pages_list if label == selected_label)
            st.session_state[_NAV_STATE_KEY] = selected_key
            st.rerun()

    with col_toggle:
        st.toggle(
            "Light" if theme == "light" else "Dark",
            key="nav_theme_toggle_switch",
            on_change=on_nav_theme_toggle_change,
        )

    st.markdown("</div>", unsafe_allow_html=True)


