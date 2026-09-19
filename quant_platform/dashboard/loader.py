"""High-tech graphical loading screen and telemetry animations for BetaScope."""

import streamlit as st


def get_loader_html(status_text: str = "SYNCHRONIZING MULTI-ASSET FEEDS") -> str:
    """Return the HTML/CSS markup for the graphical BetaScope loading screen."""
    return f"""
    <div class="betascope-loader-wrap">
        <div class="betascope-loader-core">
            <!-- Concentric Orbital Radar Rings -->
            <div class="radar-ring radar-ring-outer"></div>
            <div class="radar-ring radar-ring-mid"></div>
            <div class="radar-ring radar-ring-inner"></div>
            
            <!-- Glowing Core Logo -->
            <div class="betascope-logo-sphere">
                <span class="logo-symbol">&beta;</span>
                <div class="pulse-aura"></div>
            </div>
            
            <!-- Rotating Sweep Scanner -->
            <div class="radar-scanner"></div>
        </div>

        <!-- Typography & Brand -->
        <div class="loader-brand-title">BetaScope</div>
        <div class="loader-brand-subtitle">QUANTITATIVE MULTI-ASSET INTELLIGENCE</div>

        <!-- Graphical Telemetry Visualizer Bars -->
        <div class="loader-telemetry-bars">
            <span class="t-bar" style="--d:0.1s; --h:24px;"></span>
            <span class="t-bar" style="--d:0.3s; --h:36px;"></span>
            <span class="t-bar" style="--d:0.2s; --h:18px;"></span>
            <span class="t-bar" style="--d:0.4s; --h:42px;"></span>
            <span class="t-bar" style="--d:0.25s; --h:28px;"></span>
            <span class="t-bar" style="--d:0.5s; --h:50px;"></span>
            <span class="t-bar" style="--d:0.35s; --h:32px;"></span>
            <span class="t-bar" style="--d:0.15s; --h:20px;"></span>
            <span class="t-bar" style="--d:0.45s; --h:45px;"></span>
            <span class="t-bar" style="--d:0.2s; --h:26px;"></span>
        </div>


        <!-- Dynamic Status & Progress Line -->
        <div class="loader-status-tag">
            <span class="status-indicator-dot"></span>
            <span class="status-msg">{status_text}</span>
        </div>
        
        <div class="loader-progress-track">
            <div class="loader-progress-fill"></div>
        </div>
        
        <div class="loader-node-info">
            <span>CORE NODE: AP-SOUTH-1</span>
            <span>VECTORIZED BACKTEST READY</span>
            <span>FEED: ALPHA_CALIBRATED</span>
        </div>
    </div>
    """


def render_graphical_loader(status_text: str = "SYNCHRONIZING MULTI-ASSET FEEDS"):
    """Render the high-end graphical loader inside the current Streamlit block."""
    st.markdown(get_loader_html(status_text=status_text), unsafe_allow_html=True)
