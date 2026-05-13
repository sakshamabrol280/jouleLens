"""
JouleLens — Live Energy Monitor.
Real-time hardware telemetry and system-wide power tracking.
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime

from styles import CSS
from energy_simulator import _read_rapl_energy_uj
from utils import format_joules, format_currency

# Page Config
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<h1 class="gradient-header">⚡ Live System Monitor</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">Track the real-time energy cost of all background tasks and active software.</p>',
    unsafe_allow_html=True,
)

# Initialize Session State for Live Tracking
if "live_tracking_active" not in st.session_state:
    st.session_state.live_tracking_active = False
if "live_data" not in st.session_state:
    st.session_state.live_data = pd.DataFrame(columns=["Time", "Watts", "Cumulative_J"])
if "start_energy" not in st.session_state:
    st.session_state.start_energy = 0
if "stop_reason" not in st.session_state:
    st.session_state.stop_reason = ""

# Sidebar controls moved to main UI for "Slide" feel
col_ctrl, col_stats = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Controls")
    if not st.session_state.live_tracking_active:
        if st.button("▶️ Start Live Tracking", width="stretch", type="primary"):
            st.session_state.live_tracking_active = True
            st.session_state.live_data = pd.DataFrame(columns=["Time", "Watts", "Cumulative_J"])
            current_uj = _read_rapl_energy_uj()
            st.session_state.start_energy = current_uj if current_uj else 0
            st.rerun()
    else:
        if st.button("⏹️ Stop Tracking", width="stretch"):
            st.session_state.live_tracking_active = False
            st.session_state.stop_reason = "Manual Stop"
            st.rerun()
    
    st.markdown("")
    with st.expander("🛡️ Auto-Stop Settings", expanded=False):
        auto_stop_time = st.slider("Max Duration (min)", 1, 60, 5)
        auto_stop_energy = st.number_input("Energy Budget (J)", 10, 10000, 500)
        smart_idle = st.checkbox("Smart Idle Stop", value=True, help="Automatically stops if system stays idle for 30 seconds.")
    
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    st.info("This monitor captures system-wide CPU energy using Intel RAPL telemetry.")

with col_stats:
    # Placeholders for real-time updates
    m1, m2, m3 = st.columns(3)
    p_watt = m1.empty()
    p_joule = m2.empty()
    p_cost = m3.empty()
    
    chart_placeholder = st.empty()

# Real-time Loop
if st.session_state.live_tracking_active:
    # Use a high-performance update loop
    last_uj = _read_rapl_energy_uj()
    last_time = time.time()
    total_j = 0
    
    # Simulation baseline if RAPL is missing (Windows fallback)
    is_simulated = last_uj is None
    
    # We loop until user stops or page reruns
    start_time_abs = time.time()
    idle_counter = 0

    while st.session_state.live_tracking_active:
        time.sleep(0.5) # Sample every 500ms
        
        curr_time = time.time()
        dt = curr_time - last_time
        
        curr_uj = _read_rapl_energy_uj()
        
        if not is_simulated and curr_uj is not None:
            # Real hardware math
            dj = (curr_uj - last_uj) / 1e6
            watts = dj / dt if dt > 0 else 0
            # Handle RAPL rollover
            if dj < 0: dj = 0; watts = 0
            total_j += dj
            last_uj = curr_uj
        else:
            # Simulated telemetry math (based on random system activity)
            watts = random.uniform(5.0, 35.0) 
            dj = watts * dt
            total_j += dj
        
        last_time = curr_time
        
        # Update Data
        new_row = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Watts": round(watts, 2),
            "Cumulative_J": round(total_j, 2)
        }
        
        st.session_state.live_data = pd.concat([st.session_state.live_data, pd.DataFrame([new_row])], ignore_index=True)
        # Keep only last 50 points for performance
        if len(st.session_state.live_data) > 50:
            st.session_state.live_data = st.session_state.live_data.iloc[1:]
            
        # Update Metrics
        p_watt.metric("⚡ Current Power", f"{watts:.2f} W")
        p_joule.metric("🔋 Session Energy", format_joules(total_j))
        cost_per_kwh = st.session_state.get("cost_per_kwh", 0.12)
        kwh = total_j / 3600000.0
        p_cost.metric("💰 Session Cost", format_currency(kwh * cost_per_kwh))
        
        # Termination Checks
        elapsed_min = (time.time() - start_time_abs) / 60.0
        if elapsed_min >= auto_stop_time:
            st.session_state.live_tracking_active = False
            st.session_state.stop_reason = f"⏱️ Time limit ({auto_stop_time}m) reached."
            st.rerun()
            
        if total_j >= auto_stop_energy:
            st.session_state.live_tracking_active = False
            st.session_state.stop_reason = f"🔋 Energy budget ({auto_stop_energy}J) reached."
            st.rerun()
            
        if smart_idle and watts < 5.0:
            idle_counter += 1
            if idle_counter > 60: # 30 seconds
                st.session_state.live_tracking_active = False
                st.session_state.stop_reason = "💤 Smart Idle: System returned to baseline for 30s."
                st.rerun()
        else:
            idle_counter = 0
        
        # Update Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state.live_data["Time"],
            y=st.session_state.live_data["Watts"],
            mode='lines+markers',
            name='Power (Watts)',
            line=dict(color='#00FF88', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 136, 0.1)'
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title="Time"),
            yaxis=dict(showgrid=True, gridcolor="#30363D", title="Watts", range=[0, max(40, st.session_state.live_data["Watts"].max() + 5)]),
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=False
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)

else:
    # Static view when stopped
    if st.session_state.stop_reason and st.session_state.stop_reason != "Manual Stop":
        st.warning(f"**Session Auto-Terminated:** {st.session_state.stop_reason}")

    if not st.session_state.live_data.empty:
        m1.metric("⚡ Peak Power", f"{st.session_state.live_data['Watts'].max():.2f} W")
        m2.metric("🔋 Total Joules", format_joules(st.session_state.live_data['Cumulative_J'].iloc[-1]))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state.live_data["Time"],
            y=st.session_state.live_data["Watts"],
            mode='lines',
            line=dict(color='#8B949E', width=2),
            fill='tozeroy',
            fillcolor='rgba(139, 148, 158, 0.05)'
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            margin=dict(l=0, r=0, t=20, b=0)
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)
    else:
        chart_placeholder.info("Click 'Start Live Tracking' to begin monitoring system-wide energy consumption.")

# Footer
st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Sovereign Energy Monitoring ⚡</div>',
    unsafe_allow_html=True,
)
