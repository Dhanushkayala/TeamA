"""
QuantLab Design System — Modern High-Density Institutional Dark Theme.

Features:
- Glassmorphic surface system with subtle rim-lighting and micro-glow.
- Refined dark palette: Midnight Slate (#0a0d12), Surface (#121720), Elevated (#18202c), Border (#1e2638).
- Typography: Plus Jakarta Sans (headings) + Inter (body) + JetBrains Mono (metrics/code).
- Micro-animations: Smooth 150-250ms transitions, clean scrollbars, and tactile button hover states.
"""

import streamlit as st


def apply_custom_css() -> None:
    """Inject the QuantLab design system CSS into the Streamlit app."""
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════════
       FONTS
    ═══════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* ── Design Tokens ────────────────────────────────────────────── */
    :root {
        --bg-base:          #0a0d12;
        --bg-surface:       #121720;
        --bg-elevated:      #18202c;
        --bg-hover:         #1f293a;
        --bg-glass:         rgba(18, 23, 32, 0.85);
        --border:           #1e2638;
        --border-subtle:    rgba(255, 255, 255, 0.06);
        --border-glow:      rgba(59, 130, 246, 0.35);
        
        --accent-primary:   #3b82f6;
        --accent-primary-h: #2563eb;
        --accent-cyan:      #06b6d4;
        --accent-success:   #10b981;
        --accent-danger:    #f43f5e;
        --accent-warning:   #f59e0b;
        --accent-purple:    #8b5cf6;
        
        --text-primary:     #f1f5f9;
        --text-secondary:   #94a3b8;
        --text-muted:       #64748b;
        --text-link:        #38bdf8;
        
        --radius-xs:        4px;
        --radius-sm:        8px;
        --radius-md:        12px;
        --radius-lg:        18px;
        
        --shadow-card:      0 4px 20px rgba(0, 0, 0, 0.4), 0 1px 3px rgba(0, 0, 0, 0.2);
        --shadow-glow:      0 0 20px rgba(59, 130, 246, 0.15);
        --shadow-dropdown:  0 10px 30px rgba(0, 0, 0, 0.6);
        
        --transition-fast:  150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-std:   250ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ═══════════════════════════════════════════════════════════════
       BASE / TYPOGRAPHY
    ═══════════════════════════════════════════════════════════════ */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: var(--bg-base);
        color: var(--text-primary);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    h1, h2, h3 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.025em;
    }

    h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        color: var(--text-secondary);
        letter-spacing: -0.015em;
    }

    code, pre, .mono-font, .stMetric [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
    }

    a { color: var(--text-link); text-decoration: none; transition: color var(--transition-fast); }
    a:hover { color: var(--accent-primary); text-decoration: none; }

    /* Custom Sleek Scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* ═══════════════════════════════════════════════════════════════
       STREAMLIT LAYOUT & CONTAINERS
    ═══════════════════════════════════════════════════════════════ */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 1520px;
    }

    /* Hide Streamlit Default Header */
    [data-testid="stHeader"] {
        background: transparent !important;
        display: none !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1.2rem 1rem !important;
    }

    /* Sidebar User Pill */
    .sidebar-user-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        margin-bottom: 14px;
        box-shadow: var(--shadow-card);
    }
    .sidebar-avatar-sm {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1d4ed8, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        color: #fff;
    }
    .sidebar-user-name {
        font-size: 0.86rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
    }
    .sidebar-user-role {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin: 0;
    }

    /* Inputs, Selectboxes, and Text Areas */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stNumberInput"] > div > div > input,
    [data-testid="stTextArea"] > div > div > textarea,
    [data-testid="stMultiSelect"] > div > div {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-size: 0.88rem !important;
        transition: all var(--transition-fast) !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus,
    [data-testid="stNumberInput"] > div > div > input:focus,
    [data-testid="stSelectbox"] > div > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1rem !important;
        transition: all var(--transition-fast) !important;
        box-shadow: var(--shadow-card) !important;
    }
    .stButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--accent-primary) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #2563eb 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4) !important;
    }

    /* Dataframes & Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
        background: var(--bg-surface) !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       TOP NAVIGATION BAR
    ═══════════════════════════════════════════════════════════════ */
    .ql-navbar {
        position: sticky;
        top: 0;
        z-index: 9999;
        background: var(--bg-glass);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--border);
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 56px;
        margin-bottom: 22px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-card);
    }
    .ql-navbar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }
    .ql-navbar-logo {
        width: 32px;
        height: 32px;
        border-radius: 9px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1rem;
        color: #ffffff;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.35);
    }
    .ql-navbar-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.02em;
    }
    .ql-live-tag {
        font-size: 0.70rem;
        font-weight: 600;
        color: var(--accent-success);
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 2px 8px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .ql-live-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent-success);
        box-shadow: 0 0 8px var(--accent-success);
    }

    /* Nav Item Buttons in the Navbar Row */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn > button {
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: var(--radius-sm) !important;
        white-space: nowrap !important;
        transition: all var(--transition-fast) !important;
        box-shadow: none !important;
        transform: none !important;
        height: 38px !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn > button:hover {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn-active > button {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #60a5fa !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--accent-primary) !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       PREMIUM KPI CARDS & SECTION HERO
    ═══════════════════════════════════════════════════════════════ */
    .quant-card {
        background: var(--bg-surface);
        background: linear-gradient(180deg, rgba(22, 27, 34, 0.9) 0%, rgba(16, 21, 28, 0.95) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: var(--shadow-card);
        transition: all var(--transition-std);
        position: relative;
        overflow: hidden;
    }
    .quant-card:hover {
        border-color: rgba(59, 130, 246, 0.35);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), 0 0 15px rgba(59, 130, 246, 0.12);
    }
    .quant-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent);
    }
    .quant-card-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin-bottom: 6px;
    }
    .quant-card-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    .quant-card-sub {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-top: 6px;
        font-weight: 500;
    }

    /* Section Header Banner */
    .section-banner {
        background: linear-gradient(135deg, rgba(18, 23, 32, 0.8) 0%, rgba(14, 18, 26, 0.9) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow-card);
    }
    .section-banner-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .section-banner-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .section-banner-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .section-banner-sub {
        font-size: 0.80rem;
        color: var(--text-muted);
        margin: 2px 0 0 0;
    }

    /* Floating AI Chatbot Button & Badge */
    .floating-ai-badge {
        position: fixed;
        bottom: 74px;
        right: 28px;
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #38bdf8;
        box-shadow: var(--shadow-card);
        z-index: 9998;
        pointer-events: none;
    }
    div[data-testid="stButton"] button:has(div:contains("💬")),
    button[key="floating_corner_ai_btn"] {
        position: fixed !important;
        bottom: 24px !important;
        right: 28px !important;
        width: 52px !important;
        height: 52px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        font-size: 1.4rem !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 6px 24px rgba(37, 99, 235, 0.45) !important;
        z-index: 9999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        transition: transform var(--transition-fast), box-shadow var(--transition-fast) !important;
    }
    div[data-testid="stButton"] button:has(div:contains("💬")):hover,
    button[key="floating_corner_ai_btn"]:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 8px 30px rgba(6, 182, 212, 0.55) !important;
    }

    /* Page Fade-In Transition */
    .ql-page-content {
        animation: fadeIn 220ms ease-out forwards;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Footer Disclaimer */
    .quant-disclaimer {
        margin-top: 40px;
        padding: 12px 18px;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        font-size: 0.76rem;
        color: var(--text-muted);
        text-align: center;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)
