"""
QuantLab Authentication Module.

Provides secure, native Streamlit authentication:
  - Login / Register / Logout flows
  - Bcrypt password verification and hashing
  - Credential persistence via users_db.yaml
  - Quick 1-click Demo Account access
"""

import os
from pathlib import Path
import yaml
import bcrypt
import streamlit as st


# Path to credentials file (project root)
_YAML_PATH = Path(__file__).parents[2] / "users_db.yaml"


def _load_config() -> dict:
    """Load credentials config from YAML file, with fallback defaults."""
    if _YAML_PATH.exists():
        try:
            with open(_YAML_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "credentials" in data:
                    return data
        except Exception:
            pass

    # Fallback default configuration
    default_config = {
        "credentials": {
            "usernames": {
                "demo": {
                    "name": "Demo User",
                    "email": "demo@quantlab.io",
                    "password": bcrypt.hashpw(b"demo123", bcrypt.gensalt(12)).decode("utf-8"),
                    "role": "user",
                },
                "admin": {
                    "name": "QuantLab Admin",
                    "email": "admin@quantlab.io",
                    "password": bcrypt.hashpw(b"admin2024", bcrypt.gensalt(12)).decode("utf-8"),
                    "role": "admin",
                },
            }
        }
    }
    _save_config(default_config)
    return default_config


def _save_config(config: dict) -> None:
    """Persist credentials back to YAML."""
    try:
        with open(_YAML_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    except Exception:
        pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def get_auth_state() -> tuple[bool, str, str]:
    """
    Check current session authentication status.

    Returns:
        (is_authenticated, display_name, username)
    """
    is_auth = st.session_state.get("authentication_status", False)
    name = st.session_state.get("name", "")
    username = st.session_state.get("username", "")
    return is_auth, name, username


def render_auth_page() -> tuple[bool, str, str]:
    """
    Render the login and registration page.

    Returns:
        (is_authenticated, display_name, username)
    """
    config = _load_config()
    users = config.get("credentials", {}).get("usernames", {})

    # Check if already authenticated
    if st.session_state.get("authentication_status", False):
        return True, st.session_state.get("name", "User"), st.session_state.get("username", "user")

    # ── Centered Auth Box Layout ─────────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 1.8, 1])

    with col_c:
        st.markdown("""
        <div class="auth-page-header">
            <div class="auth-logo">
                <div class="auth-logo-icon">Q</div>
                <div>
                    <div class="auth-logo-title">QuantLab</div>
                    <div class="auth-logo-sub">Quantitative Multi-Asset Intelligence</div>
                </div>
            </div>
            <p class="auth-tagline">
                Institutional-grade quantitative analytics, backtesting,
                and AI-driven market intelligence — all in one platform.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick 1-Click Demo Login
        col_demo1, col_demo2 = st.columns([1, 1])
        with col_demo1:
            if st.button("🚀 Quick Login (Demo)", key="btn_quick_demo", use_container_width=True, type="primary"):
                st.session_state["authentication_status"] = True
                st.session_state["username"] = "demo"
                st.session_state["name"] = users.get("demo", {}).get("name", "Demo User")
                st.rerun()

        with col_demo2:
            if st.button("👑 Quick Login (Admin)", key="btn_quick_admin", use_container_width=True):
                st.session_state["authentication_status"] = True
                st.session_state["username"] = "admin"
                st.session_state["name"] = users.get("admin", {}).get("name", "QuantLab Admin")
                st.rerun()

        st.markdown("<div style='margin: 12px 0 16px 0; text-align: center; color: #484f58; font-size: 0.8rem;'>─── OR SIGN IN WITH CREDENTIALS ───</div>", unsafe_allow_html=True)

        login_tab, register_tab = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input("Username", placeholder="e.g. demo", key="form_user")
                password_input = st.text_input("Password", type="password", placeholder="e.g. demo123", key="form_pass")
                submit_login = st.form_submit_button("Sign In →", use_container_width=True)

            if submit_login:
                u_clean = username_input.strip()
                if not u_clean or not password_input:
                    st.error("Please enter both username and password.")
                elif u_clean not in users:
                    st.error("❌ Username not found.")
                else:
                    stored_hash = users[u_clean].get("password", "")
                    if verify_password(password_input, stored_hash):
                        st.session_state["authentication_status"] = True
                        st.session_state["username"] = u_clean
                        st.session_state["name"] = users[u_clean].get("name", u_clean)
                        st.success(f"Welcome back, {st.session_state['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password.")

            st.markdown(
                "<p style='color:#7d8590; font-size:0.82rem; margin-top:12px;'>"
                "<strong style='color:#adbac7;'>Demo account:</strong> "
                "username <code>demo</code> · password <code>demo123</code>"
                "</p>",
                unsafe_allow_html=True,
            )

        with register_tab:
            with st.form("register_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", placeholder="e.g. John Doe", key="reg_name")
                reg_user = st.text_input("Username", placeholder="e.g. jdoe", key="reg_user")
                reg_email = st.text_input("Email", placeholder="e.g. john@example.com", key="reg_email")
                reg_pass = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="reg_pass")
                reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
                submit_reg = st.form_submit_button("Create Account ✨", use_container_width=True)

            if submit_reg:
                u_clean = reg_user.strip().lower()
                if not reg_name.strip() or not u_clean or not reg_email.strip() or not reg_pass:
                    st.error("All fields are required.")
                elif len(reg_pass) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match.")
                elif u_clean in users:
                    st.error(f"Username '{u_clean}' already exists. Please choose another.")
                else:
                    users[u_clean] = {
                        "name": reg_name.strip(),
                        "email": reg_email.strip(),
                        "password": hash_password(reg_pass),
                        "role": "user",
                    }
                    config["credentials"]["usernames"] = users
                    _save_config(config)

                    st.session_state["authentication_status"] = True
                    st.session_state["username"] = u_clean
                    st.session_state["name"] = reg_name.strip()
                    st.success("🎉 Account created successfully! Logging you in...")
                    st.rerun()

    return False, "", ""


def render_logout_button(button_key: str = "logout_btn") -> None:
    """Render a clean Sign Out button."""
    if st.button("🚪 Sign Out", key=button_key, use_container_width=True):
        st.session_state["authentication_status"] = False
        st.session_state["username"] = ""
        st.session_state["name"] = ""
        for key in list(st.session_state.keys()):
            if key.startswith("saved_"):
                del st.session_state[key]
        st.rerun()
