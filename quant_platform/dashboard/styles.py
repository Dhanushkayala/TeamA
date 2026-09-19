"""
QuantLab Design System — High-Density Institutional Theme Engine.

Supports fully functional and dynamic:
- 🌙 Dark Mode (Midnight Slate, Obsidian, Glassmorphism, Micro-rim lighting)
- ☀️ Light Mode (Refined Slate/White, Clean Typography, High Contrast, Tactile Borders)
"""

import streamlit as st


def apply_custom_css(theme: str = None) -> None:
    """Inject the dynamic QuantLab design system CSS into the Streamlit app."""
    active_theme = theme or st.session_state.get("ql_theme", "dark")

    if active_theme == "light":
        tokens_css = """
        --bg-base:          #f1f5f9;
        --bg-surface:       #ffffff;
        --bg-elevated:      #f8fafc;
        --bg-hover:         #e2e8f0;
        --bg-glass:         rgba(255, 255, 255, 0.97);
        --border:           #cbd5e1;
        --border-subtle:    rgba(0, 0, 0, 0.07);
        --border-glow:      rgba(37, 99, 235, 0.25);

        --accent-primary:   #2563eb;
        --accent-primary-h: #1d4ed8;
        --accent-cyan:      #0891b2;
        --accent-success:   #059669;
        --accent-danger:    #e11d48;
        --accent-warning:   #d97706;
        --accent-purple:    #7c3aed;

        --text-primary:     #0f172a;
        --text-secondary:   #334155;
        --text-muted:       #64748b;
        --text-link:        #2563eb;

        --shadow-card:      0 2px 10px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03);
        --shadow-glow:      0 0 15px rgba(37, 99, 235, 0.12);
        --shadow-dropdown:  0 10px 25px rgba(0, 0, 0, 0.10);

        --card-grad:        linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        --banner-grad:      linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        --table-header-bg:  #f1f5f9;
        --table-row-hover:  #f8fafc;
        --scrollbar-thumb:  #cbd5e1;
        """
        app_bg_css = """
        /* LIGHT MODE — full app background & text */
        [data-testid="stAppViewContainer"],
        .stApp,
        [data-testid="stMain"] {
            background-color: #f1f5f9 !important;
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div {
            background-color: #ffffff !important;
        }

        /* All Streamlit text elements in light mode */
        [data-testid="stMain"] p,
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] h4,
        [data-testid="stMain"] h5,
        [data-testid="stMain"] h6,
        [data-testid="stMain"] span,
        [data-testid="stMain"] label {
            color: #0f172a !important;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #0f172a !important;
        }
        [data-testid="stCaptionContainer"] p { color: #64748b !important; }
        [data-testid="stMetricValue"] { color: #0f172a !important; }
        [data-testid="stMetricLabel"] { color: #334155 !important; }
        [data-testid="stMetricDelta"] span { color: inherit !important; }

        /* Light mode inputs */
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stSelectbox"] > div > div > div {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        [data-testid="stMultiSelect"] > div > div { background-color: #ffffff !important; }
        [data-testid="stMultiSelect"] span { color: #0f172a !important; }

        /* Light mode radio & checkbox */
        .stRadio > div > label > div > p { color: #0f172a !important; }
        .stCheckbox > label > div > p { color: #0f172a !important; }

        /* Light mode buttons */
        .stButton > button {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }

        /* Light mode tabs */
        [data-testid="stTabs"] button { color: #64748b !important; }
        [data-testid="stTabs"] button[aria-selected="true"] { color: #2563eb !important; }

        /* Slider labels */
        [data-testid="stSlider"] p,
        [data-testid="stSlider"] span[data-testid="stTickBarMin"],
        [data-testid="stSlider"] span[data-testid="stTickBarMax"] {
            color: #0f172a !important;
        }

        /* Date inputs */
        [data-testid="stDateInput"] input {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }

        /* Expander */
        .streamlit-expanderHeader { background-color: #f8fafc !important; color: #0f172a !important; }
        .streamlit-expanderContent { background-color: #ffffff !important; }
        """
    else:
        # Dark Theme
        tokens_css = """
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

        --shadow-card:      0 4px 20px rgba(0, 0, 0, 0.4), 0 1px 3px rgba(0, 0, 0, 0.2);
        --shadow-glow:      0 0 20px rgba(59, 130, 246, 0.15);
        --shadow-dropdown:  0 10px 30px rgba(0, 0, 0, 0.6);

        --card-grad:        linear-gradient(180deg, rgba(22, 27, 34, 0.9) 0%, rgba(16, 21, 28, 0.95) 100%);
        --banner-grad:      linear-gradient(135deg, rgba(18, 23, 32, 0.8) 0%, rgba(14, 18, 26, 0.9) 100%);
        --table-header-bg:  #18202c;
        --table-row-hover:  #1a2230;
        --scrollbar-thumb:  #1e2638;
        """
        app_bg_css = """
        /* DARK MODE — full app background */
        [data-testid="stAppViewContainer"],
        .stApp,
        [data-testid="stMain"] {
            background-color: #0a0d12 !important;
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div {
            background-color: #121720 !important;
        }

        /* Dark mode inputs */
        [data-testid="stSelectbox"] > div > div {
            background-color: #121720 !important;
            color: #f1f5f9 !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            background-color: #121720 !important;
            color: #f1f5f9 !important;
        }
        [data-testid="stMultiSelect"] > div > div {
            background-color: #121720 !important;
            color: #f1f5f9 !important;
        }
        """

    st.markdown(f"""
    <style>
    /* ═══════════════════════════════════════════════════════════════
       FONTS
    ═══════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* ── Design Tokens ────────────────────────────────────────────── */
    :root {{
        {tokens_css}
        
        --radius-xs:        4px;
        --radius-sm:        8px;
        --radius-md:        12px;
        --radius-lg:        18px;
        
        --transition-fast:  150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-std:   250ms cubic-bezier(0.4, 0, 0.2, 1);
    }}

    {app_bg_css}

    /* ═══════════════════════════════════════════════════════════════
       BASE / TYPOGRAPHY (non-conflicting with Streamlit widgets)
    ═══════════════════════════════════════════════════════════════ */
    html, body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: var(--bg-base);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    h1, h2, h3 {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.025em;
    }}

    h4, h5, h6 {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        color: var(--text-secondary);
        letter-spacing: -0.015em;
    }}

    /* Custom HTML elements use CSS variables — do NOT override Streamlit's native components here */
    .quant-card *, .section-banner *, .styled-table *, .profile-header *,
    .achievement-card *, .auth-card *, .sidebar-user-pill * {{
        color: inherit;
    }}

    code, pre, .mono-font, .stMetric [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace;
    }}

    a {{ color: var(--text-link); text-decoration: none; transition: color var(--transition-fast); }}
    a:hover {{ color: var(--accent-primary); text-decoration: none; }}

    /* Custom Sleek Scrollbars */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-base); }}
    ::-webkit-scrollbar-thumb {{ background: var(--scrollbar-thumb); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

    /* ═══════════════════════════════════════════════════════════════
       STREAMLIT LAYOUT & CONTAINERS
    ═══════════════════════════════════════════════════════════════ */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 1520px;
    }}

    /* Hide Streamlit Default Header */
    [data-testid="stHeader"] {{
        background: transparent !important;
        display: none !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stSidebar"] .block-container {{
        padding: 1.2rem 1rem !important;
    }}

    /* Sidebar User Pill */
    .sidebar-user-pill {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin-bottom: 14px;
        box-shadow: var(--shadow-card);
    }}
    .sidebar-avatar-sm {{
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
    }}
    .sidebar-user-name {{
        font-size: 0.86rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
    }}
    .sidebar-user-role {{
        font-size: 0.72rem;
        color: var(--text-muted);
        margin: 0;
    }}

    /* Inputs, Selectboxes, and Text Areas */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stNumberInput"] > div > div > input,
    [data-testid="stTextArea"] > div > div > textarea,
    [data-testid="stMultiSelect"] > div > div {{
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-size: 0.88rem !important;
        transition: all var(--transition-fast) !important;
    }}
    [data-testid="stTextInput"] > div > div > input:focus,
    [data-testid="stNumberInput"] > div > div > input:focus,
    [data-testid="stSelectbox"] > div > div:focus-within {{
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1rem !important;
        transition: all var(--transition-fast) !important;
        box-shadow: var(--shadow-card) !important;
    }}
    .stButton > button:hover {{
        background: var(--bg-hover) !important;
        border-color: var(--accent-primary) !important;
        color: var(--text-primary) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12) !important;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--accent-primary) 0%, #2563eb 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4) !important;
    }}

    /* Dataframes & Tables */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
        background: var(--bg-surface) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════
       TOP NAVIGATION BAR
    ═══════════════════════════════════════════════════════════════ */
    .ql-navbar {{
        position: sticky;
        top: 0;
        z-index: 9999;
        background: var(--bg-glass);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border);
        padding: 0 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 56px;
        margin-bottom: 18px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-card);
    }}
    .ql-navbar-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }}
    .ql-navbar-logo {{
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
    }}
    .ql-navbar-name {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.02em;
    }}
    .ql-live-tag {{
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
    }}
    .ql-live-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent-success);
        box-shadow: 0 0 8px var(--accent-success);
    }}

    /* Nav Item Buttons in the Navbar Row */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn > button {{
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        padding: 8px 10px !important;
        border-radius: var(--radius-sm) !important;
        white-space: nowrap !important;
        transition: all var(--transition-fast) !important;
        box-shadow: none !important;
        transform: none !important;
        height: 38px !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn > button:hover {{
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .ql-nav-btn-active > button {{
        background: rgba(37, 99, 235, 0.12) !important;
        color: var(--accent-primary) !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--accent-primary) !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    }}

    /* ═══════════════════════════════════════════════════════════════
       PREMIUM KPI CARDS & SECTION HERO
    ═══════════════════════════════════════════════════════════════ */
    .quant-card {{
        background: var(--card-grad);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: var(--shadow-card);
        transition: all var(--transition-std);
        position: relative;
        overflow: hidden;
    }}
    .quant-card:hover {{
        border-color: var(--accent-primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-card), 0 0 15px rgba(37, 99, 235, 0.12);
    }}
    .quant-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    }}
    .quant-card-title {{
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin-bottom: 6px;
    }}
    .quant-card-value {{
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}
    .quant-card-sub {{
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-top: 6px;
        font-weight: 500;
    }}

    /* Section Header Banner */
    .section-banner {{
        background: var(--banner-grad);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow-card);
    }}
    .section-banner-left {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .section-banner-icon {{
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: rgba(37, 99, 235, 0.10);
        border: 1px solid rgba(37, 99, 235, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }}
    .section-banner-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .section-banner-sub {{
        font-size: 0.80rem;
        color: var(--text-muted);
        margin: 2px 0 0 0;
    }}

    /* Styled Tables */
    .styled-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.86rem;
        margin-top: 12px;
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        overflow: hidden;
    }}
    .styled-table th {{
        background: var(--table-header-bg);
        color: var(--text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 1px solid var(--border);
    }}
    .styled-table td {{
        padding: 10px 14px;
        border-bottom: 1px solid var(--border-subtle);
        color: var(--text-primary);
    }}
    .styled-table tr:hover {{
        background: var(--table-row-hover);
    }}

    /* Profile View Components */
    .profile-header {{
        background: var(--card-grad);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 22px;
        margin-bottom: 22px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: var(--shadow-card);
    }}
    .profile-avatar {{
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.6rem;
        color: #fff;
        flex-shrink: 0;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
    }}
    .profile-name {{
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .profile-meta {{
        font-size: 0.84rem;
        color: var(--text-muted);
        margin-top: 4px;
    }}

    .achievement-card {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 16px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        box-shadow: var(--shadow-card);
    }}
    .achievement-icon {{
        font-size: 1.6rem;
    }}
    .achievement-info h5 {{
        margin: 0;
        font-size: 0.92rem;
        font-weight: 600;
        color: var(--text-primary);
    }}
    .achievement-info p {{
        margin: 2px 0 0 0;
        font-size: 0.78rem;
        color: var(--text-muted);
    }}

    /* Auth Login Cards */
    .auth-card {{
        background: var(--card-grad);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 32px 28px;
        box-shadow: var(--shadow-dropdown);
    }}
    .auth-logo {{
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.5rem;
        color: #ffffff;
        margin-bottom: 14px;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
    }}

    /* Badges */
    .quant-badge {{
        font-size: 0.76rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    .quant-badge-blue   {{ background: rgba(37,99,235,0.12); color: var(--accent-primary); border: 1px solid rgba(37,99,235,0.25); }}
    .quant-badge-gold   {{ background: rgba(245,158,11,0.12); color: var(--accent-warning); border: 1px solid rgba(245,158,11,0.25); }}
    .quant-badge-green  {{ background: rgba(16,185,129,0.12); color: var(--accent-success); border: 1px solid rgba(16,185,129,0.25); }}
    .quant-badge-purple {{ background: rgba(139,92,246,0.12); color: var(--accent-purple); border: 1px solid rgba(139,92,246,0.25); }}

    /* Tabs Styling */
    [data-testid="stTabs"] button {{
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 16px !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    }}
    [data-testid="stTabs"] button:hover {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: var(--accent-primary) !important;
        border-bottom: 2px solid var(--accent-primary) !important;
    }}

    /* Floating AI Chatbot Button & Badge */
    .floating-ai-badge {{
        position: fixed;
        bottom: 74px;
        right: 28px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--accent-primary);
        box-shadow: var(--shadow-card);
        z-index: 9998;
        pointer-events: none;
    }}
    div[data-testid="stButton"] button:has(div:contains("💬")),
    button[key="floating_corner_ai_btn"] {{
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
    }}
    div[data-testid="stButton"] button:has(div:contains("💬")):hover,
    button[key="floating_corner_ai_btn"]:hover {{
        transform: scale(1.08) !important;
        box-shadow: 0 8px 30px rgba(6, 182, 212, 0.55) !important;
    }}

    /* Page Fade-In Transition */
    .ql-page-content {{
        animation: fadeIn 200ms ease-out forwards;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Footer Disclaimer */
    .quant-disclaimer {{
        margin-top: 40px;
        padding: 12px 18px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        font-size: 0.76rem;
        color: var(--text-muted);
        text-align: center;
        line-height: 1.5;
    }}
    </style>
    """, unsafe_allow_html=True)
