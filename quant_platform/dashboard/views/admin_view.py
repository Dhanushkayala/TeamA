import streamlit as st

def render_admin_view():
    """
    Render the Admin Dashboard.
    """
    st.markdown("""
    <div style="padding: 20px 0;">
        <h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">
            Admin Dashboard
        </h2>
        <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 24px;">
            Manage platform settings, view user activity, and monitor system health.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: var(--card-bg); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 20px;">
            <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">Active Users</div>
            <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">24</div>
            <div style="font-size: 0.85rem; color: #10b981; margin-top: 8px;">+12% this week</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background-color: var(--card-bg); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 20px;">
            <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">System Status</div>
            <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">Online</div>
            <div style="font-size: 0.85rem; color: #10b981; margin-top: 8px;">All systems operational</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="background-color: var(--card-bg); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 20px;">
            <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">Data Feeds</div>
            <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">Synced</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 8px;">Last update: 2 mins ago</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("Additional administrative features (user management, API keys, audit logs) will be displayed here.")
