"""High-tech graphical loading screen and telemetry animations for BetaScope."""

import streamlit as st


def get_loader_html(status_text: str = "SYNCHRONIZING MULTI-ASSET FEEDS & CALIBRATING ENGINE...") -> str:
    """Return the HTML/CSS markup for the ultra-premium BetaScope loading animation."""
    return f"""
    <div class="betascope-loader-wrap">
        <!-- Floating Ambient Glow Orbs -->
        <div class="loader-ambient-glow glow-1"></div>
        <div class="loader-ambient-glow glow-2"></div>

        <div class="betascope-loader-core">
            <!-- Concentric Orbital Rings with Segmented Markers -->
            <div class="radar-ring radar-ring-outer"></div>
            <div class="radar-ring radar-ring-mid"></div>
            <div class="radar-ring radar-ring-inner"></div>
            <div class="radar-ring radar-ring-dots"></div>
            
            <!-- Rotating Holographic Radar Scanner -->
            <div class="radar-scanner"></div>

            <!-- Glowing Beta Central Core Sphere -->
            <div class="betascope-logo-sphere">
                <span class="logo-symbol">&beta;</span>
                <div class="pulse-aura"></div>
                <div class="pulse-aura-outer"></div>
            </div>
        </div>

        <!-- Typography & Brand -->
        <div class="loader-brand-title">
            <span class="brand-beta">Beta</span><span class="brand-scope">Scope</span>
        </div>
        <div class="loader-brand-subtitle">
            <span class="sub-dot"></span> QUANTITATIVE FINANCIAL INTELLIGENCE PLATFORM
        </div>

        <!-- High-Tech Spectrum Audio-Visualizer Bars (16 Dynamic Channels) -->
        <div class="loader-telemetry-bars">
            <span class="t-bar" style="--d:0.05s; --h:24px;"></span>
            <span class="t-bar" style="--d:0.25s; --h:38px;"></span>
            <span class="t-bar" style="--d:0.15s; --h:18px;"></span>
            <span class="t-bar" style="--d:0.35s; --h:44px;"></span>
            <span class="t-bar" style="--d:0.20s; --h:28px;"></span>
            <span class="t-bar" style="--d:0.45s; --h:52px;"></span>
            <span class="t-bar" style="--d:0.30s; --h:34px;"></span>
            <span class="t-bar" style="--d:0.10s; --h:22px;"></span>
            <span class="t-bar" style="--d:0.40s; --h:48px;"></span>
            <span class="t-bar" style="--d:0.18s; --h:30px;"></span>
            <span class="t-bar" style="--d:0.32s; --h:42px;"></span>
            <span class="t-bar" style="--d:0.12s; --h:20px;"></span>
            <span class="t-bar" style="--d:0.28s; --h:36px;"></span>
            <span class="t-bar" style="--d:0.48s; --h:50px;"></span>
            <span class="t-bar" style="--d:0.22s; --h:26px;"></span>
            <span class="t-bar" style="--d:0.08s; --h:16px;"></span>
        </div>

        <!-- Active Status Tag -->
        <div class="loader-status-tag">
            <span class="status-indicator-dot"></span>
            <span class="status-msg">{status_text}</span>
        </div>
        
        <!-- Glowing Cyberpunk Progress Track -->
        <div class="loader-progress-track">
            <div class="loader-progress-fill"></div>
            <div class="loader-progress-glow"></div>
        </div>
        
        <!-- Institutional Terminal Telemetry Badges -->
        <div class="loader-node-info">
            <div class="telemetry-pill"><span class="pill-dot"></span> CORE ENGINE: ONLINE</div>
            <div class="telemetry-pill"><span class="pill-dot"></span> CALENDAR ALIGNMENT: ACTIVE</div>
            <div class="telemetry-pill"><span class="pill-dot"></span> LATENCY: ~12ms</div>
            <div class="telemetry-pill"><span class="pill-dot"></span> REGIME CLASSIFIER: SYNCED</div>
        </div>
    </div>
    """


def render_graphical_loader(status_text: str = "SYNCHRONIZING MULTI-ASSET FEEDS & CALIBRATING ENGINE..."):
    """Render the high-end graphical loader inside the current Streamlit block."""
    st.markdown(get_loader_html(status_text=status_text), unsafe_allow_html=True)

