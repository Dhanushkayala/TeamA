"""
BetaScope Authentication Module.

Provides Google OAuth2 authentication:
  - Sign in / Sign up via Google
  - Admin role check
"""

import os
import requests
import streamlit as st
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")


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


def get_user_role() -> str:
    """
    Get the current user's role.
    """
    return st.session_state.get("role", "user")


def render_auth_page() -> tuple[bool, str, str]:
    """
    Render the Google OAuth login page.

    Returns:
        (is_authenticated, display_name, username)
    """
    if st.session_state.get("authentication_status", False):
        return True, st.session_state.get("name", "User"), st.session_state.get("username", "user")

    # Check for OAuth callback
    if "code" in st.query_params:
        code = st.query_params["code"]
        try:
            # Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
            token_r = requests.post(token_url, data=token_data)
            token_r.raise_for_status()
            access_token = token_r.json().get("access_token")

            # Get user info
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            userinfo_r = requests.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            userinfo_r.raise_for_status()
            user_data = userinfo_r.json()

            # Set session state
            st.session_state["authentication_status"] = True
            st.session_state["name"] = user_data.get("name", "User")
            email = user_data.get("email", "")
            st.session_state["username"] = email
            
            # Check Admin role
            is_admin = (email and email.lower() == ADMIN_EMAIL.lower())
            st.session_state["role"] = "admin" if is_admin else "user"
            
            if is_admin:
                st.session_state["ql_active_page"] = "admin"
            
            # Clear query params
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error("Authentication failed. Please check your Google OAuth credentials or try again.")
            st.query_params.clear()

    # ── Centered Auth Box Layout ─────────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 1.8, 1])

    with col_c:
        st.markdown("""
        <div class="auth-page-header">
            <div class="auth-logo">
                <div class="auth-logo-icon">&beta;</div>
                <div>
                    <div class="auth-logo-title">BetaScope</div>
                    <div class="auth-logo-sub">Quantitative Multi-Asset Intelligence</div>
                </div>
            </div>
            <p class="auth-tagline">
                Institutional-grade quantitative analytics, backtesting,
                and AI-driven market intelligence — all in one platform.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            st.warning("Google OAuth credentials are not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.")

        # Generate Auth URL
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account"
        }
        login_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

        # Custom Google Login Button
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-top: 30px; margin-bottom: 30px;">
                <a href="{login_url}" target="_self" style="text-decoration: none;">
                    <div style="background-color: var(--card-bg); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 24px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google Logo" style="width: 24px; height: 24px;">
                        <span style="color: var(--text-primary); font-weight: 600; font-family: 'Inter', sans-serif;">Sign in with Google</span>
                    </div>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    return False, "", ""


def render_logout_button(button_key: str = "logout_btn") -> None:
    """Render a clean Sign Out button."""
    if st.button("Sign Out", key=button_key, use_container_width=True):
        st.session_state["authentication_status"] = False
        st.session_state["username"] = ""
        st.session_state["name"] = ""
        st.session_state["role"] = "user"
        for key in list(st.session_state.keys()):
            if key.startswith("saved_"):
                del st.session_state[key]
        st.rerun()
