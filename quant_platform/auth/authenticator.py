"""
QuantLab Authentication Module.

Wraps streamlit_authenticator to provide:
  - Login / Register / Logout flows
  - Persistent cookie-based sessions
  - Credential storage via users_db.yaml
"""

import yaml
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path


# Path to the credentials file (project root)
_YAML_PATH = Path(__file__).parents[2] / "users_db.yaml"


def _load_config() -> dict:
    """Load raw YAML config from disk."""
    with open(_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_config(config: dict) -> None:
    """Persist updated credentials back to YAML."""
    with open(_YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def _get_authenticator() -> tuple["stauth.Authenticate", dict]:
    """
    Build (or reuse from session_state) the Authenticate instance.

    The authenticator creates a CookieManager which must live outside
    any @st.cache_resource context, so we store it in session_state.
    """
    if "ql_authenticator" not in st.session_state:
        config = _load_config()
        authenticator = stauth.Authenticate(
            credentials=config["credentials"],
            cookie_name=config["cookie"]["name"],
            cookie_key=config["cookie"]["key"],
            cookie_expiry_days=config["cookie"]["expiry_days"],
            pre_authorized=config.get("pre-authorized", {}).get("emails", []),
        )
        st.session_state["ql_authenticator"] = authenticator
        st.session_state["ql_config"] = config

    return st.session_state["ql_authenticator"], st.session_state["ql_config"]


def render_auth_page() -> tuple[bool, str, str]:
    """
    Render the login/register page.

    Returns:
        (is_authenticated: bool, name: str, username: str)
    """
    authenticator, config = _get_authenticator()

    # ── Custom Auth Page Layout ───────────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 1.6, 1])
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

        login_tab, register_tab = st.tabs(["🔐 Sign In", "✨ Create Account"])

    name: str | None = None
    authentication_status: bool | None = None
    username: str | None = None

    with col_c:
        with login_tab:
            try:
                name, authentication_status, username = authenticator.login(
                    fields={
                        "Form name": "",
                        "Username": "Username",
                        "Password": "Password",
                        "Login": "Sign In →",
                    },
                    location="main",
                )
            except Exception as e:
                st.error(f"Login error: {e}")
                return False, "", ""

            if authentication_status is False:
                st.error("❌ Incorrect username or password.")
            elif authentication_status is None:
                st.markdown(
                    "<p style='color:#7d8590; font-size:0.85rem; margin-top:8px;'>"
                    "Enter your credentials to access the platform.<br>"
                    "<strong style='color:#adbac7;'>Demo account:</strong> "
                    "username <code>demo</code> · password <code>demo123</code>"
                    "</p>",
                    unsafe_allow_html=True,
                )

        with register_tab:
            try:
                result = authenticator.register_user(
                    fields={
                        "Form name": "",
                        "First name": "First Name",
                        "Last name": "Last Name",
                        "Email": "Email Address",
                        "Username": "Choose a Username",
                        "Password": "Password",
                        "Repeat password": "Confirm Password",
                        "Register": "Create Account →",
                    },
                    location="main",
                    pre_authorization=False,
                )
                # result can be (email, username, name) or None
                if result and result[0]:
                    # Reload fresh config and save
                    fresh_config = _load_config()
                    _save_config(fresh_config)
                    # Force re-create authenticator next run
                    if "ql_authenticator" in st.session_state:
                        del st.session_state["ql_authenticator"]
                        del st.session_state["ql_config"]
                    st.success(
                        f"✅ Account created for **{result[2]}**! "
                        "Switch to the Sign In tab to log in."
                    )
            except stauth.RegisterError as e:
                st.error(f"Registration error: {e}")
            except Exception as e:
                if "already" in str(e).lower():
                    st.error("Username or email already registered.")
                else:
                    st.error(f"Unexpected error: {e}")

    is_auth = authentication_status is True
    return is_auth, (name or ""), (username or "")


def render_logout_button(key: str = "sidebar_logout") -> None:
    """Render a logout button in the sidebar."""
    authenticator, _ = _get_authenticator()
    try:
        authenticator.logout(button_name="Sign Out", location="sidebar", key=key)
    except Exception:
        if st.sidebar.button("Sign Out", key=key):
            for k in ["authentication_status", "name", "username",
                      "ql_authenticator", "ql_config"]:
                st.session_state.pop(k, None)
            st.rerun()


def get_auth_state() -> tuple[bool, str, str]:
    """Return current (is_authenticated, name, username) from session state."""
    status = st.session_state.get("authentication_status")
    name = st.session_state.get("name") or ""
    username = st.session_state.get("username") or ""
    return (status is True), name, username
