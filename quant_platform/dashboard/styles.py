"""
QuantLab Design System — Refined Dark Theme.

Color palette: GitHub dark-inspired, no neons.
Typography: Plus Jakarta Sans (headings) + Inter (body) + JetBrains Mono (code/numbers).
Animations: ≤300ms cubic-bezier, calm and fluid — no harsh glow or infinite neon pulse.
"""

import streamlit as st


def apply_custom_css() -> None:
    """Inject the QuantLab design system CSS into the Streamlit app."""
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════════
       FONTS
    ═══════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Design Tokens ────────────────────────────────────────────── */
    :root {
        --bg-base:         #0d1117;
        --bg-surface:      #161b22;
        --bg-elevated:     #1c2333;
        --bg-hover:        #21262d;
        --border:          #30363d;
        --border-subtle:   #21262d;
        --accent-primary:  #3b82f6;
        --accent-primary-h:#2563eb;
        --accent-success:  #22c55e;
        --accent-danger:   #ef4444;
        --accent-warm:     #f59e0b;
        --accent-purple:   #8b5cf6;
        --text-primary:    #e6edf3;
        --text-secondary:  #adbac7;
        --text-muted:      #7d8590;
        --text-link:       #58a6ff;
        --radius-sm:       6px;
        --radius-md:       10px;
        --radius-lg:       16px;
        --shadow-sm:       0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
        --shadow-md:       0 4px 12px rgba(0,0,0,0.5), 0 2px 6px rgba(0,0,0,0.3);
        --shadow-lg:       0 10px 30px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-std:  250ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
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
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.025em;
    }

    h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-secondary);
    }

    code, pre, .mono-font, .stMetric [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
    }

    a { color: var(--text-link); text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* ═══════════════════════════════════════════════════════════════
       STREAMLIT OVERRIDES
    ═══════════════════════════════════════════════════════════════ */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1440px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1rem;
    }

    /* Remove extra whitespace above page */
    .main .block-container { padding-top: 1rem; }

    /* Streamlit header toolbar */
    [data-testid="stHeader"] {
        background-color: var(--bg-base);
        border-bottom: 1px solid var(--border-subtle);
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        transition: border-color var(--transition-std);
    }
    [data-testid="stExpander"]:hover {
        border-color: var(--accent-primary);
    }

    /* Selectbox / inputs */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stNumberInput"] > div > div > input,
    [data-testid="stTextArea"] > div > div > textarea {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        transition: border-color var(--transition-fast) !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus,
    [data-testid="stNumberInput"] > div > div > input:focus,
    [data-testid="stTextArea"] > div > div > textarea:focus {
        border-color: var(--accent-primary) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    /* Slider */
    [data-testid="stSlider"] > div > div > div > div {
        background-color: var(--accent-primary) !important;
    }

    /* Generic buttons */
    .stButton > button {
        background: var(--bg-elevated);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        font-weight: 500;
        font-size: 0.9rem;
        transition: all var(--transition-fast);
        padding: 0.45rem 1rem;
    }
    .stButton > button:hover {
        background: var(--bg-hover);
        border-color: var(--accent-primary);
        color: var(--text-primary);
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Primary button (type="primary") */
    .stButton > button[kind="primary"] {
        background: var(--accent-primary) !important;
        border-color: var(--accent-primary) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-primary-h) !important;
        border-color: var(--accent-primary-h) !important;
        box-shadow: 0 4px 12px rgba(59,130,246,0.35) !important;
    }

    /* Multiselect */
    [data-baseweb="tag"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        color: var(--text-link) !important;
        border-radius: 4px !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       TABS
    ═══════════════════════════════════════════════════════════════ */
    /* ═══════════════════════════════════════════════════════════════
       TOP NAVIGATION BAR
    ═══════════════════════════════════════════════════════════════ */

    /* Hide Streamlit's default header toolbar to make room */
    [data-testid="stHeader"] { display: none !important; }

    /* Main content shifts up since header is hidden */
    .main .block-container { padding-top: 0 !important; }

    /* Sticky nav wrapper */
    .ql-navbar {
        position: sticky;
        top: 0;
        z-index: 9999;
        background: rgba(13, 17, 23, 0.9);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
        padding: 0 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 54px;
        margin-bottom: 20px;
    }

    /* Left: logo section */
    .ql-navbar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        flex-shrink: 0;
    }
    .ql-navbar-logo {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: linear-gradient(135deg, #1d4ed8, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.95rem;
        color: #fff;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .ql-navbar-name {
        font-size: 0.98rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.025em;
    }

    /* Center: nav items */
    .ql-navbar-items {
        display: flex;
        align-items: center;
        gap: 2px;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }

    /* Nav item buttons */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn > button {
        background: transparent !important;
        border: none !important;
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 6px 12px !important;
        border-radius: var(--radius-sm) !important;
        white-space: nowrap !important;
        transition: color var(--transition-fast), background var(--transition-fast) !important;
        box-shadow: none !important;
        transform: none !important;
        height: 36px !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn > button:hover {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Active nav item */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn-active > button {
        background: rgba(59, 130, 246, 0.12) !important;
        color: #58a6ff !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--accent-primary) !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    }

    /* Pull the nav button row (stHorizontalBlock) up into the navbar visual area.
       The .ql-navbar div is 54px tall; we shift the button row up by ~66px so it
       sits centred inside that bar, then add a left offset to skip past the logo. */
    .ql-navbar + div [data-testid="stHorizontalBlock"],
    .ql-navbar ~ div [data-testid="stHorizontalBlock"]:first-of-type {
        position: relative;
        margin-top: -66px !important;
        padding: 0 0 0 180px !important;
        z-index: 10000;
        background: transparent !important;
    }

    /* Remove the extra gap the column row would otherwise add */
    .ql-navbar ~ div [data-testid="stHorizontalBlock"]:first-of-type + div {
        margin-top: 16px !important;
    }

    /* Each column in the nav row: no padding, auto height */
    .ql-navbar ~ div [data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"] {
        padding: 0 1px !important;
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
    }

    /* Page content fade-in on nav switch */
    @keyframes page-fade {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .ql-page-content {
        animation: page-fade 0.2s ease-out both;
    }

    /* Suppress st.tabs completely (we replaced with navbar) */
    .stTabs { display: none !important; }

    /* ═══════════════════════════════════════════════════════════════
       METRIC CARDS
    ═══════════════════════════════════════════════════════════════ */
    .quant-card {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 16px 18px;
        margin-bottom: 12px;
        transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
        position: relative;
        overflow: hidden;
    }
    .quant-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--card-accent, var(--accent-primary));
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        opacity: 0;
        transition: opacity var(--transition-std);
    }
    .quant-card:hover {
        transform: translateY(-3px);
        border-color: var(--border-subtle);
        box-shadow: var(--shadow-md);
    }
    .quant-card:hover::before {
        opacity: 1;
    }

    .quant-card-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 6px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    .quant-card-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.2;
    }
    .quant-card-sub {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 5px;
        font-weight: 400;
    }

    /* Delta chips */
    .delta-positive {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        color: var(--accent-success);
        font-size: 0.82rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .delta-negative {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        color: var(--accent-danger);
        font-size: 0.82rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ═══════════════════════════════════════════════════════════════
       SECTION HEADERS
    ═══════════════════════════════════════════════════════════════ */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 24px 0 12px 0;
    }
    .section-header-icon {
        width: 36px;
        height: 36px;
        border-radius: var(--radius-sm);
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .section-header-text h4 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .section-header-text p {
        margin: 2px 0 0 0;
        font-size: 0.82rem;
        color: var(--text-muted);
    }

    /* ═══════════════════════════════════════════════════════════════
       BADGE / PILL TAGS
    ═══════════════════════════════════════════════════════════════ */
    .quant-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .quant-badge-blue  { background: rgba(59,130,246,0.12); color: #58a6ff; border: 1px solid rgba(59,130,246,0.3); }
    .quant-badge-gold  { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
    .quant-badge-green { background: rgba(34,197,94,0.12);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3);  }
    .quant-badge-red   { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3);  }
    .quant-badge-purple{ background: rgba(139,92,246,0.12); color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }

    /* ═══════════════════════════════════════════════════════════════
       TABLES
    ═══════════════════════════════════════════════════════════════ */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 0.88rem;
        border-radius: var(--radius-md);
        overflow: hidden;
        border: 1px solid var(--border);
    }
    .styled-table thead tr {
        background: var(--bg-elevated);
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .styled-table th, .styled-table td {
        padding: 10px 14px;
        text-align: left;
        border-bottom: 1px solid var(--border-subtle);
    }
    .styled-table tbody tr:last-child td {
        border-bottom: none;
    }
    .styled-table tbody tr:hover {
        background: var(--bg-elevated);
    }
    .styled-table td {
        color: var(--text-primary);
    }

    /* ═══════════════════════════════════════════════════════════════
       DISCLAIMER FOOTER
    ═══════════════════════════════════════════════════════════════ */
    .quant-disclaimer {
        text-align: center;
        font-size: 0.78rem;
        color: var(--text-muted);
        padding: 20px 0 12px 0;
        border-top: 1px solid var(--border-subtle);
        margin-top: 48px;
        line-height: 1.6;
    }

    /* ═══════════════════════════════════════════════════════════════
       FLOATING AI CHATBOT FAB (Bottom-Right)
    ═══════════════════════════════════════════════════════════════ */
    @keyframes fab-float {
        0%, 100% { transform: translateY(0px); box-shadow: 0 8px 24px rgba(59,130,246,0.3), 0 4px 12px rgba(0,0,0,0.5); }
        50%       { transform: translateY(-5px); box-shadow: 0 14px 32px rgba(59,130,246,0.4), 0 8px 20px rgba(0,0,0,0.5); }
    }

    @keyframes badge-slide-in {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes online-pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.5; }
    }

    /* FAB container — fixed to bottom right */
    div.st-key-floating_corner_ai_btn,
    div[data-testid="stElementContainer"]:has(div.st-key-floating_corner_ai_btn) {
        position: fixed !important;
        bottom: 28px !important;
        right: 28px !important;
        z-index: 999999 !important;
        width: 60px !important;
        height: 60px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div.st-key-floating_corner_ai_btn button {
        position: fixed !important;
        bottom: 28px !important;
        right: 28px !important;
        z-index: 999999 !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 50%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: 1.5px solid rgba(255,255,255,0.25) !important;
        font-size: 1.6rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        animation: fab-float 4s ease-in-out infinite !important;
        transition: transform var(--transition-std), filter var(--transition-std) !important;
        cursor: pointer !important;
    }
    div.st-key-floating_corner_ai_btn button:hover {
        transform: scale(1.1) translateY(-2px) !important;
        filter: brightness(1.15) !important;
        animation-play-state: paused !important;
    }
    div.st-key-floating_corner_ai_btn button:active {
        transform: scale(0.94) !important;
    }

    /* Status badge above FAB */
    .floating-ai-badge {
        position: fixed !important;
        bottom: 98px !important;
        right: 20px !important;
        z-index: 999998 !important;
        background: var(--bg-elevated);
        color: var(--text-primary);
        font-size: 0.78rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        pointer-events: none;
        display: flex;
        align-items: center;
        gap: 7px;
        animation: badge-slide-in 0.4s ease-out both;
        font-family: 'Inter', sans-serif;
    }
    .floating-ai-badge::after {
        content: '';
        position: absolute;
        bottom: -5px;
        right: 24px;
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid var(--bg-elevated);
    }
    .online-indicator {
        width: 7px;
        height: 7px;
        background: var(--accent-success);
        border-radius: 50%;
        display: inline-block;
        animation: online-pulse 2.5s ease-in-out infinite;
    }

    /* ═══════════════════════════════════════════════════════════════
       CHAT DIALOG (QuantBot interface)
    ═══════════════════════════════════════════════════════════════ */
    .chat-app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 18px;
        background: var(--bg-elevated);
        border-bottom: 1px solid var(--border);
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        margin-bottom: 16px;
    }
    .chat-app-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .chat-app-subtitle {
        font-size: 0.73rem;
        color: var(--accent-success);
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Bubbles */
    @keyframes bubble-in {
        from { opacity: 0; transform: translateY(8px) scale(0.97); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    .chat-msg-row {
        display: flex;
        width: 100%;
        margin-bottom: 12px;
        animation: bubble-in 0.22s ease-out both;
    }
    .chat-msg-row-bot  { justify-content: flex-start; }
    .chat-msg-row-user { justify-content: flex-end; }

    .chat-bubble-bot {
        background: var(--bg-elevated);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 14px 14px 14px 3px;
        padding: 12px 16px;
        max-width: 86%;
        font-size: 0.9rem;
        line-height: 1.55;
        box-shadow: var(--shadow-sm);
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
        color: #ffffff;
        border-radius: 14px 14px 3px 14px;
        padding: 11px 16px;
        max-width: 82%;
        font-size: 0.9rem;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(59,130,246,0.3);
        font-weight: 500;
    }

    /* Suggestion chips */
    .chat-chips-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 10px 0 14px 0;
    }
    .stButton.chip-btn > button {
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 20px !important;
        padding: 5px 14px !important;
        font-size: 0.80rem !important;
        font-weight: 500 !important;
        transition: all var(--transition-fast) !important;
    }
    .stButton.chip-btn > button:hover {
        background: rgba(59,130,246,0.12) !important;
        color: var(--text-link) !important;
        border-color: rgba(59,130,246,0.4) !important;
        transform: translateY(-2px) !important;
    }

    /* Context pill */
    .chat-context-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.25);
        color: var(--text-link);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .chat-scroll-area {
        max-height: 400px;
        overflow-y: auto;
        padding-right: 6px;
        margin-bottom: 12px;
        scrollbar-width: thin;
        scrollbar-color: var(--border) transparent;
    }
    .chat-scroll-area::-webkit-scrollbar { width: 4px; }
    .chat-scroll-area::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    /* Form input cleanup */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       AUTHENTICATION PAGE
    ═══════════════════════════════════════════════════════════════ */
    .auth-page-header {
        text-align: center;
        padding: 48px 24px 32px;
        max-width: 480px;
        margin: 0 auto 8px;
    }
    .auth-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 14px;
        margin-bottom: 16px;
    }
    .auth-logo-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1d4ed8, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.5rem;
        color: #fff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        box-shadow: 0 4px 16px rgba(59,130,246,0.4);
    }
    .auth-logo-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.04em;
    }
    .auth-logo-sub {
        font-size: 0.80rem;
        color: var(--text-muted);
        font-weight: 400;
        margin-top: 2px;
    }
    .auth-tagline {
        font-size: 0.92rem;
        color: var(--text-muted);
        line-height: 1.6;
        max-width: 380px;
        margin: 0 auto;
    }

    /* ═══════════════════════════════════════════════════════════════
       USER PROFILE
    ═══════════════════════════════════════════════════════════════ */
    .profile-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1d4ed8, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 800;
        color: #fff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        box-shadow: 0 4px 16px rgba(59,130,246,0.3);
        flex-shrink: 0;
    }
    .profile-header {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 24px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        margin-bottom: 20px;
    }
    .profile-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin: 0;
    }
    .profile-meta {
        font-size: 0.83rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* Achievement cards */
    .achievement-card {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 16px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        transition: transform var(--transition-fast), border-color var(--transition-fast);
    }
    .achievement-card:hover {
        transform: translateX(4px);
        border-color: var(--accent-primary);
    }
    .achievement-icon {
        font-size: 1.8rem;
        width: 44px;
        text-align: center;
        flex-shrink: 0;
    }
    .achievement-info h5 {
        margin: 0 0 2px 0;
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .achievement-info p {
        margin: 0;
        font-size: 0.78rem;
        color: var(--text-muted);
    }

    /* Rarity chips */
    .rarity-common   { color: var(--text-muted); font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
    .rarity-uncommon { color: var(--accent-success); font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
    .rarity-rare     { color: var(--text-link); font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
    .rarity-epic     { color: var(--accent-purple); font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }

    /* Sidebar user pill */
    .sidebar-user-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin-bottom: 14px;
    }
    .sidebar-avatar-sm {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1d4ed8, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 700;
        color: #fff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        flex-shrink: 0;
    }
    .sidebar-user-name {
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin: 0;
    }
    .sidebar-user-role {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)
