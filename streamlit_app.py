"""
Streamlit Frontend for AI Dashboard Agent
Generate KPI dashboards with natural language
"""

import streamlit as st
import requests
import uuid
from typing import Optional

# ── Page Configuration ──────────────────────────────────────

st.set_page_config(
    page_title="AI Dashboard Agent",
    page_icon="📊",
    layout="wide"
)

# ── Simple Custom CSS ──────────────────────────────────────

st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ── API Configuration ──────────────────────────────────────

API_URL = st.secrets.get("API_URL", "http://localhost:8000")
DASHBOARD_ENDPOINT = f"{API_URL}/dashboard"

# ── Session State Initialization ──────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4().hex[:12]}"

if "dashboard_html" not in st.session_state:
    st.session_state.dashboard_html = None

# ── Helper Functions ──────────────────────────────────────

def call_dashboard_api(kpis: list[str]) -> Optional[dict]:
    """Call the backend API to generate a dashboard."""
    try:
        payload = {
            "kpis": kpis,
            "session_id": st.session_state.session_id,
            "verbose": False
        }
        
        with st.spinner("⏳ Generating your dashboard..."):
            response = requests.post(
                DASHBOARD_ENDPOINT,
                json=payload,
                timeout=120
            )
            
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ API Error: {response.status_code}")
            if response.text:
                st.error(f"Details: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_URL}")
        st.info("Make sure the backend is running: `uvicorn main:app --port 8000`")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# ── Header ──────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>📊 AI Dashboard Agent</h1>
    <p>Generate beautiful KPI dashboards from natural language</p>
</div>
""", unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────

if st.session_state.dashboard_html is None:
    # Input Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        kpi_input = st.text_input(
            "📝 Enter KPIs (comma-separated)",
            placeholder="e.g., revenue, churn rate, top customers",
            key="kpi_input"
        )
    
    with col2:
        st.write("")
        st.write("")
        submit_button = st.button("🚀 Generate", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    # Process Request
    if submit_button:
        if kpi_input:
            kpis = [k.strip() for k in kpi_input.split(",") if k.strip()]
            if kpis:
                result = call_dashboard_api(kpis)
                if result:
                    st.session_state.dashboard_html = result['html']
                    st.rerun()
            else:
                st.error("Please enter at least one KPI")
        else:
            st.error("Please enter KPIs")

else:
    # Display the Generated Dashboard
    st.components.v1.html(st.session_state.dashboard_html, height=900, scrolling=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔄 Generate Another Dashboard"):
            st.session_state.dashboard_html = None
            st.session_state.session_id = f"session-{uuid.uuid4().hex[:12]}"
            st.rerun()
    
    with col2:
        st.download_button(
            label="⬇️ Download HTML",
            data=st.session_state.dashboard_html,
            file_name=f"dashboard_{st.session_state.session_id}.html",
            mime="text/html",
            use_container_width=True
        )
