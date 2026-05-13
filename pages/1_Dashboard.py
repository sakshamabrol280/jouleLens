"""
JouleLens — Dashboard Page.
Overview hub with aggregate stats, charts, and carbon intensity.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime

from styles import CSS
from database import get_aggregate_stats, get_all_runs, init_db
from carbon_api import get_carbon_intensity, get_grid_status
from utils import format_joules, format_currency, format_co2, score_to_color
from energy_simulator import get_emissions_equivalents

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Ensure DB is initialized
init_db()



# Header
st.markdown('<h1 class="gradient-header">JouleLens Dashboard</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">Energy is the Final Currency of Computing</p>',
    unsafe_allow_html=True,
)

# ===== KPI METRICS =====
stats = get_aggregate_stats()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("⚡ Total Joules Profiled", format_joules(stats["total_joules"]))
with c2:
    st.metric("🌿 Total CO₂ Emitted", format_co2(stats["total_co2"]))
with c3:
    st.metric("💰 Total Estimated Cost", format_currency(stats["total_cost"]))
with c4:
    st.metric("🔬 Profiling Runs", str(stats["total_runs"]))

st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# ===== CHARTS =====
runs = get_all_runs()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### 📈 Energy Cost Over Time")
    if runs:
        last_10 = list(reversed(runs[:10]))
        df = pd.DataFrame({
            "Run": [f"#{r['id']}" for r in last_10],
            "Joules": [r["total_joules"] for r in last_10],
            "Timestamp": [r["timestamp"] for r in last_10],
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Timestamp"], y=df["Joules"],
            mode="lines+markers",
            line=dict(color="#00FF88", width=3),
            marker=dict(size=8, color="#00FF88", line=dict(width=2, color="#0D1117")),
            fill="tozeroy",
            fillcolor="rgba(0,255,136,0.08)",
            name="Energy (J)",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="", showgrid=False, color="#8B949E"),
            yaxis=dict(title="Joules", showgrid=True, gridcolor="#30363D", color="#8B949E"),
            height=350,
            margin=dict(l=40, r=20, t=20, b=40),
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No profiling data yet. Run your first profile!")

with chart_col2:
    st.markdown("### 🍩 Energy by Category")
    categories = ["Loops & Iteration", "I/O Operations", "Compute / Math", "Memory Allocation"]
    values = [35, 20, 30, 15]
    colors = ["#FF4B4B", "#F0A500", "#58A6FF", "#3FB950"]
    
    fig2 = go.Figure(data=[go.Pie(
        labels=categories, values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0D1117", width=2)),
        textfont=dict(color="#E6EDF3", size=12),
        textinfo="label+percent",
    )])
    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        annotations=[dict(text="Energy<br>Mix", x=0.5, y=0.5, font_size=14,
                          font_color="#8B949E", showarrow=False)],
    )
    st.plotly_chart(fig2, width="stretch")

st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# ===== CARBON INTENSITY GAUGE =====
gauge_col, info_col = st.columns([1, 1])

with gauge_col:
    st.markdown("### 🌍 Current Grid Carbon Intensity")
    region = st.session_state.get("selected_region", "US-CAL-CISO")
    carbon_data = get_carbon_intensity(region)
    ci = carbon_data["carbon_intensity"]
    status_label, status_color = get_grid_status(ci)
    
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ci,
        number=dict(suffix=" gCO₂/kWh", font=dict(size=22, color="#E6EDF3")),
        gauge=dict(
            axis=dict(range=[0, 700], tickcolor="#8B949E", tickfont=dict(color="#8B949E")),
            bar=dict(color="#58A6FF"),
            bgcolor="#1C2128",
            steps=[
                dict(range=[0, 100], color="rgba(0,255,136,0.25)"),
                dict(range=[100, 250], color="rgba(240,165,0,0.25)"),
                dict(range=[250, 700], color="rgba(255,75,75,0.25)"),
            ],
            threshold=dict(line=dict(color="#00FF88", width=3), thickness=0.8, value=ci),
        ),
    ))
    fig3.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=30, r=30, t=30, b=10),
    )
    st.plotly_chart(fig3, width="stretch")

with info_col:
    st.markdown("### 🌱 Emissions Impact")
    if runs:
        last_run = runs[0]
        co2 = last_run.get("co2_grams", 0)
        total_co2 = stats["total_co2"]
        
        equivalents = get_emissions_equivalents(total_co2)
        st.markdown(f"**Total emissions from all {stats['total_runs']} runs:**")
        for eq in equivalents:
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{eq}")
    else:
        st.info("Run a profile to see emissions impact.")
    
    st.markdown("")
    if st.button("⚡ Start Profiling →", key="dashboard_start_profiling"):
        st.switch_page("pages/2_Profiler.py")

# Footer
st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Making Every Joule Count ⚡</div>',
    unsafe_allow_html=True,
)
