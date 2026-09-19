"""
BetaScope Authentication Module.

Provides Google OAuth2 authentication:
  - Sign in / Sign up via Google
  - Admin role check
  - Supports both .env and Streamlit Cloud st.secrets
"""

import os
import requests
import streamlit as st
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    """Retrieve config from st.secrets first, then os.getenv, then default."""
    if hasattr(st, "secrets") and key in st.secrets:
        return str(st.secrets[key])
    return os.getenv(key, default)


def get_google_credentials():
    client_id = _get_config("GOOGLE_CLIENT_ID", "")
    client_secret = _get_config("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = _get_config("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    admin_email = _get_config("ADMIN_EMAIL", "admin@example.com")
    return client_id, client_secret, redirect_uri, admin_email


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
    """Get the current user's role."""
    return st.session_state.get("role", "user")


def render_auth_page() -> tuple[bool, str, str]:
    """
    Render the Google OAuth login page.

    Returns:
        (is_authenticated, display_name, username)
    """
    if st.session_state.get("authentication_status", False):
        return True, st.session_state.get("name", "User"), st.session_state.get("username", "user")

    client_id, client_secret, redirect_uri, admin_email = get_google_credentials()

    # Check for OAuth callback code
    if "code" in st.query_params:
        code = st.query_params["code"]
        try:
            # Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
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
            is_admin = bool(email and email.strip().lower() == admin_email.strip().lower())
            st.session_state["role"] = "admin" if is_admin else "user"
            
            if is_admin:
                st.session_state["ql_active_page"] = "admin"
            
            # Clear query params and rerun
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Authentication failed ({type(e).__name__}). Please verify your credentials and Authorized Redirect URIs in Google Cloud Console.")
            st.query_params.clear()

    # ── Centered Auth Box Layout ─────────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 2, 1])

    with col_c:
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px 20px 20px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 18px; background: linear-gradient(135deg, #2563eb, #7c3aed); color: #ffffff; font-size: 2rem; font-weight: 800; box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4); margin-bottom: 20px;">
                &beta;
            </div>
            <h1 style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; margin: 0 0 8px 0; background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                BetaScope
            </h1>
            <p style="font-size: 0.95rem; font-weight: 600; color: #06b6d4; text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 16px 0;">
                Quantitative Multi-Asset Intelligence
            </p>
            <p style="font-size: 0.92rem; color: #94a3b8; max-width: 480px; margin: 0 auto 30px auto; line-height: 1.6;">
                Institutional-grade quantitative analytics, algorithmic backtesting, and AI-driven market intelligence — all in one platform.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not client_id or not client_secret:
            st.warning(
                "Google OAuth credentials are not configured.\n\n"
                "• **Local testing**: Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in your `.env` file.\n\n"
                "• **Streamlit Cloud**: Add them to **App Settings → Secrets**."
            )

        # Generate Auth URL
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account"
        }
        login_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

        # Clean Google Login Button with embedded Vector SVG
        google_svg = """<svg width="20" height="20" viewBox="0 0 48 48" style="vertical-align: middle;"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>"""

        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-top: 10px; margin-bottom: 40px;">
                <a href="{login_url}" target="_self" style="text-decoration: none; width: 100%; max-width: 320px;">
                    <div style="background: #ffffff; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 14px 24px; display: flex; align-items: center; justify-content: center; gap: 12px; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);">
                        {google_svg}
                        <span style="color: #1f2937; font-weight: 700; font-size: 0.95rem; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;">Sign in with Google</span>
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

