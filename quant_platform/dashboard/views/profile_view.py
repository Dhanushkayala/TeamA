import streamlit as st
import pandas as pd
from quant_platform.auth.user_store import ACHIEVEMENTS, load_profile, get_recent_sessions
from quant_platform.dashboard.components import render_section_banner, render_metric_card


def render_profile_view(username: str, display_name: str) -> None:
    """Render the full My Profile page for the currently logged-in user."""

    profile = load_profile(username, display_name)
    sessions = get_recent_sessions(username, n=10)
    initials = "".join(w[0].upper() for w in (display_name or username).split()[:2])

    render_section_banner(
        title=f"Trader Profile: {display_name or username}",
        subtitle=f"@{username} · Member since {profile.get('joined', '—')} · Quantitative research portfolio & achievements.",
        badge_text="USER REPUTATION & AUDIT",
    )

    # ── Profile Header ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar">{initials}</div>
        <div>
            <p class="profile-name">{display_name or username}</p>
            <div class="profile-meta">
                @{username} &nbsp;·&nbsp; Member since {profile.get("joined", "—")}
            </div>
            <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                <span class="quant-badge quant-badge-blue">⚡ {profile.get("total_sessions", 0)} Sessions</span>
                <span class="quant-badge quant-badge-gold">📊 {len(profile.get("assets_analyzed", []))} Assets</span>
                <span class="quant-badge quant-badge-purple">🧭 {len(profile.get("strategies_run", {}))} Strategies</span>
                <span class="quant-badge quant-badge-green">🏅 {len(profile.get("achievements", []))} Achievements</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── Left Column: Stats ────────────────────────────────────────────────────
    with col_left:
        st.markdown("""
        <div class="section-header">
            <div class="section-header-icon">📈</div>
            <div class="section-header-text">
                <h4>Platform Stats</h4>
                <p>Your quantitative research summary</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            render_metric_card("Total Sessions", str(profile.get("total_sessions", 0)), "Completed backtest sessions", color="accent")
            render_metric_card("Assets Analyzed", str(len(profile.get("assets_analyzed", []))), ", ".join(profile.get("assets_analyzed", [])[:3]) or "—", color="default")
        with sc2:
            render_metric_card("Strategies Run", str(sum(profile.get("strategies_run", {}).values())), ", ".join(profile.get("strategies_run", {}).keys()) or "—", color="positive")
            if sessions:
                best = max(sessions, key=lambda x: x.get("sharpe", 0))
                render_metric_card("Best Backtest Sharpe", f"{best.get('sharpe', 0):.2f}", f"{best.get('asset', '—')} · {best.get('strategy', '—')}", color="accent")
            else:
                render_metric_card("Best Backtest Sharpe", "—", "No sessions recorded", color="default")


    # ── Right Column: Achievements ────────────────────────────────────────────
    with col_right:
        earned_ids = set(profile.get("achievements", []))
        earned = [a for k, a in ACHIEVEMENTS.items() if k in earned_ids]
        locked = [a for k, a in ACHIEVEMENTS.items() if k not in earned_ids]

        st.markdown("""
        <div class="section-header">
            <div class="section-header-icon">🏅</div>
            <div class="section-header-text">
                <h4>Achievements</h4>
                <p>Unlock by exploring the platform</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if earned:
            for ach in earned:
                st.markdown(f"""
                <div class="achievement-card">
                    <div class="achievement-icon">{ach["icon"]}</div>
                    <div class="achievement-info">
                        <h5>{ach["title"]}</h5>
                        <p>{ach["description"]}</p>
                        <span class="rarity-{ach['rarity']}">{ach["rarity"]}</span>
                    </div>
                </div>
                <div style="height:6px;"></div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='color:var(--text-muted); font-size:0.88rem;'>No achievements yet — run a backtest to earn your first one!</p>",
                unsafe_allow_html=True,
            )

        if locked:
            with st.expander(f"🔒 {len(locked)} Locked Achievements"):
                for ach in locked:
                    st.markdown(f"""
                    <div class="achievement-card" style="opacity:0.45; filter:grayscale(0.6);">
                        <div class="achievement-icon">{ach["icon"]}</div>
                        <div class="achievement-info">
                            <h5>{ach["title"]}</h5>
                            <p>{ach["description"]}</p>
                            <span class="rarity-{ach['rarity']}">{ach["rarity"]}</span>
                        </div>
                    </div>
                    <div style="height:6px;"></div>
                    """, unsafe_allow_html=True)

    # ── Session History ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon">🕐</div>
        <div class="section-header-text">
            <h4>Recent Session History</h4>
            <p>Your last 10 backtest sessions</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if sessions:
        rows_html = ""
        for s in sessions:
            date_str = s.get("date", "")[:16].replace("T", " ")
            sharpe_val = s.get("sharpe", 0)
            ret_val = s.get("total_return_pct", 0)
            mdd_val = s.get("max_drawdown_pct", 0)

            sharpe_color = "var(--accent-success)" if sharpe_val >= 1.0 else ("var(--accent-warm)" if sharpe_val >= 0 else "var(--accent-danger)")
            ret_color    = "var(--accent-success)" if ret_val >= 0 else "var(--accent-danger)"
            mdd_color    = "var(--accent-danger)"

            rows_html += f"""
            <tr>
                <td style="color:var(--text-muted); font-size:0.78rem;">{date_str}</td>
                <td><strong>{s.get("asset", "—")}</strong></td>
                <td>{s.get("strategy", "—")}</td>
                <td style="color:{sharpe_color}; font-family:'JetBrains Mono',monospace; font-weight:600;">{sharpe_val:.2f}</td>
                <td style="color:{ret_color}; font-family:'JetBrains Mono',monospace; font-weight:600;">{ret_val:+.1f}%</td>
                <td style="color:{mdd_color}; font-family:'JetBrains Mono',monospace; font-weight:600;">{mdd_val:.1f}%</td>
            </tr>
            """

        st.markdown(f"""
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Date</th><th>Asset</th><th>Strategy</th>
                    <th>Sharpe</th><th>Return</th><th>Max DD</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            "<p style='color:var(--text-muted); font-size:0.88rem; padding:12px 0;'>"
            "No sessions recorded yet. Run a backtest and come back here!</p>",
            unsafe_allow_html=True,
        )
