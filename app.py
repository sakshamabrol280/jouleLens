"""
JouleLens — Main Application Entry Point.
Multi-page Streamlit app with sidebar navigation.
"""

import streamlit as st

# Page config MUST be the first Streamlit call
st.set_page_config(
    page_title="JouleLens",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import CSS
from database import init_db, get_all_runs
from mock_data import seed_mock_data
from carbon_api import get_carbon_intensity, get_grid_status
from utils import get_region_options

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Initialize database
init_db()


# Initialize session state defaults
defaults = {
    "selected_region": "US-CAL-CISO",
    "cost_per_kwh": 0.12,
    "current_code": "",
    "last_profiling_result": None,
    "last_run_id": None,
    "dark_mode": True,
    "confirm_clear": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ JouleLens</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-version">v1.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    
    # Region selector
    regions = get_region_options()
    region_names = list(regions.keys())
    region_codes = list(regions.values())
    
    current_idx = 0
    if st.session_state.selected_region in region_codes:
        current_idx = region_codes.index(st.session_state.selected_region)
    
    selected_name = st.selectbox(
        "🌍 Grid Region",
        region_names,
        index=current_idx,
        key="region_selector",
    )
    st.session_state.selected_region = regions[selected_name]
    
    # Cost per kWh
    st.session_state.cost_per_kwh = st.slider(
        "💰 Cost per kWh (₹)",
        min_value=0.01,
        max_value=20.0,
        value=float(st.session_state.cost_per_kwh),
        step=0.01,
        format="%.2f",
    )
    
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    
    # Live carbon intensity widget
    carbon_data = get_carbon_intensity(st.session_state.selected_region)
    ci = carbon_data["carbon_intensity"]
    status_label, status_color = get_grid_status(ci)
    is_mock = carbon_data["is_mock"]
    
    dot_class = "live-dot"
    if status_color == "red":
        dot_class = "live-dot live-dot-red"
    elif status_color == "orange":
        dot_class = "live-dot live-dot-yellow"
    
    mock_tag = ' <span style="opacity:0.5;font-size:0.7rem;">(mock)</span>' if is_mock else ''
    
    st.markdown(f'''
    <div class="carbon-widget">
        <div class="cw-label">LIVE CARBON INTENSITY{mock_tag}</div>
        <div class="cw-value" style="color:{status_color == "green" and "#00FF88" or status_color == "orange" and "#F0A500" or "#FF4B4B"}">
            <span class="{dot_class}"></span>
            {ci:.0f} gCO₂/kWh
        </div>
        <div style="font-size:0.85rem;margin-top:4px;">{status_label}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#8B949E;font-size:0.75rem;padding:1rem 0;">'
        'Powered by JouleLens AI<br/>Making Every Joule Count ⚡</div>',
        unsafe_allow_html=True,
    )

# ===== MAIN PAGE (Landing) =====
st.markdown('<h1 class="gradient-header">⚡ JouleLens</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">The energy profiler that makes every Joule visible, actionable, and accountable.</p>',
    unsafe_allow_html=True,
)

r1_col1, r1_col2 = st.columns(2)
with r1_col1:
    st.markdown("""
    <a href="Profiler" target="_self" style="text-decoration:none;">
    <div class="metric-card">
        <div class="metric-label">🔬 PROFILE</div>
        <div class="metric-value" style="font-size:1.1rem;">Energy Analysis</div>
        <div class="metric-delta">Measure real code energy cost</div>
    </div>
    </a>
    """, unsafe_allow_html=True)
    
with r1_col2:
    st.markdown("""
    <a href="Refactor" target="_self" style="text-decoration:none;">
    <div class="metric-card">
        <div class="metric-label">🤖 REFACTOR</div>
        <div class="metric-value" style="font-size:1.1rem;">AI Optimization</div>
        <div class="metric-delta">Gemini-powered green refactoring</div>
    </div>
    </a>
    """, unsafe_allow_html=True)

r2_col1, r2_col2 = st.columns(2)
with r2_col1:
    st.markdown("""
    <a href="Scheduler" target="_self" style="text-decoration:none;">
    <div class="metric-card">
        <div class="metric-label">🌍 SCHEDULE</div>
        <div class="metric-value" style="font-size:1.1rem;">Carbon Aware</div>
        <div class="metric-delta">Run workloads when the grid is clean</div>
    </div>
    </a>
    """, unsafe_allow_html=True)

with r2_col2:
    st.markdown("""
    <a href="Live_Monitor" target="_self" style="text-decoration:none;">
    <div class="metric-card">
        <div class="metric-label">📊 LIVE MONITOR</div>
        <div class="metric-value" style="font-size:1.1rem;">System Telemetry</div>
        <div class="metric-delta">Track real-time background tasks</div>
    </div>
    </a>
    """, unsafe_allow_html=True)

st.markdown("")
st.info("👈 **Use the sidebar pages to navigate** — Dashboard, Profiler, AI Refactor, Carbon Scheduler, History, and Live Monitor.")

st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Making Every Joule Count ⚡</div>',
    unsafe_allow_html=True,
)
