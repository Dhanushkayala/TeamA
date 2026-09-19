"""
User Profile View — My Profile tab.

Shows: user stats, strategy distribution donut, Sharpe progression, achievements, and session history.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from quant_platform.auth.user_store import ACHIEVEMENTS, load_profile, get_recent_sessions
from quant_platform.dashboard.components import apply_plotly_theme


def render_profile_view(username: str, display_name: str) -> None:
    """Render the full My Profile page for the currently logged-in user."""

    profile = load_profile(username, display_name)
    sessions = get_recent_sessions(username, n=15)
    initials = "".join(w[0].upper() for w in (display_name or username).split()[:2])

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

    # ── Left Column: Stats & Charts ───────────────────────────────────────────
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

        stats = [
            ("Total Sessions", str(profile.get("total_sessions", 0)), "Completed backtest sessions"),
            ("Assets Analyzed", str(len(profile.get("assets_analyzed", []))), ", ".join(profile.get("assets_analyzed", [])[:4]) or "—"),
            ("Strategies Run", str(sum(profile.get("strategies_run", {}).values())), ", ".join(profile.get("strategies_run", {}).keys()) or "—"),
        ]
        for title, val, sub in stats:
            st.markdown(f"""
            <div class="quant-card">
                <div class="quant-card-title">{title}</div>
                <div class="quant-card-value">{val}</div>
                <div class="quant-card-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

        # Strategy Model Allocation Donut
        strat_dict = profile.get("strategies_run", {})
        if strat_dict and sum(strat_dict.values()) > 0:
            st.markdown("##### 🧭 Strategy Usage Breakdown")
            fig_strat_donut = go.Figure(data=[go.Pie(
                labels=list(strat_dict.keys()),
                values=list(strat_dict.values()),
                hole=0.55,
                marker=dict(colors=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"], line=dict(color="#0d1117", width=2)),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Runs: %{value}<br>Share: %{percent}<extra></extra>",
            )])
            apply_plotly_theme(fig_strat_donut, height=260)
            fig_strat_donut.update_layout(showlegend=False)
            st.plotly_chart(fig_strat_donut, use_container_width=True)

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
                        <span class="rarity-{ach['rarity']}">{ach['rarity']}</span>
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
                            <span class="rarity-{ach['rarity']}">{ach['rarity']}</span>
                        </div>
                    </div>
                    <div style="height:6px;"></div>
                    """, unsafe_allow_html=True)

    # ── Session History with Sharpe Progression Bar Chart ────────────────────
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon">🕐</div>
        <div class="section-header-text">
            <h4>Recent Session History & Performance Progression</h4>
            <p>Your historical backtest records and Sharpe ratio progression</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if sessions:
        # Sharpe Progression Bar Chart
        session_dates = [s.get("date", "")[:10] for s in sessions][::-1]
        session_sharpes = [s.get("sharpe", 0.0) for s in sessions][::-1]
        session_assets = [f"{s.get('asset', '')} ({s.get('strategy', '')})" for s in sessions][::-1]
        session_colors = ["#10b981" if sh >= 1.0 else ("#f59e0b" if sh >= 0 else "#ef4444") for sh in session_sharpes]

        fig_prog = go.Figure()
        fig_prog.add_trace(go.Bar(
            x=[f"#{i+1} {session_assets[i]}" for i in range(len(session_sharpes))],
            y=session_sharpes,
            marker_color=session_colors,
            text=[f"{sh:.2f}" for sh in session_sharpes],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Sharpe: %{y:.2f}<extra></extra>",
        ))
        fig_prog.add_hline(y=1.0, line_dash="dash", line_color="#10b981", annotation_text="Benchmark Sharpe (1.0)")
        apply_plotly_theme(fig_prog, title="Historical Backtest Sharpe Ratio Progression", height=280)
        fig_prog.update_layout(yaxis_title="Sharpe Ratio")
        st.plotly_chart(fig_prog, use_container_width=True)

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
