import streamlit as st

APP_TITLE = "SCOPE | Strategic Crime Observation & Prediction Engine"
APP_ICON = "🛡️"

DISCLAIMER_TEXT = "This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."

CUSTOM_CSS = """
<style>
    /* Main Theme Light Professional Palette */
    .stApp {
        background-color: #FFFFFF;
        color: #0F172A;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Cards and KPI Containers */
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1D4ED8;
    }
    
    .metric-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Headers & Text */
    h1, h2, h3 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1D4ED8 0%, #2563EB 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1E40AF 0%, #1D4ED8 100%);
        box-shadow: 0 2px 6px rgba(29, 78, 216, 0.3);
    }
    
    /* Footer Disclaimer */
    .footer-disclaimer {
        padding: 12px;
        background-color: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: #475569;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
    }
</style>
"""

def setup_page_config(page_title=None):
    st.set_page_config(
        page_title=f"{page_title} - SCOPE" if page_title else APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_sidebar_footer():
    st.sidebar.markdown("---")
    st.sidebar.caption(f"⚠️ **Disclaimer**:\n{DISCLAIMER_TEXT}")
