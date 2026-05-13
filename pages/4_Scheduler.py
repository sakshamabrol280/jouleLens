"""
JouleLens — Carbon Scheduler Page.
Live carbon intensity, 24h forecast, and scheduling recommendations.
Also initializes the database for safety.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from styles import CSS
from carbon_api import (
    get_carbon_intensity, get_carbon_forecast,
    get_best_window, get_grid_status, ZONE_NAMES,
)
from energy_simulator import get_emissions_equivalents
from utils import get_region_options, format_co2
from database import init_db

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Ensure DB is initialized
init_db()

# Header
st.markdown('<h1 class="gradient-header">🌍 Carbon Scheduler</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">Schedule workloads when the grid is greenest</p>',
    unsafe_allow_html=True,
)

# ===== REGION SELECTOR =====
regions = get_region_options()
region_names = list(regions.keys())
region_codes = list(regions.values())

current_idx = 0
current_region = st.session_state.get("selected_region", "US-CAL-CISO")
if current_region in region_codes:
    current_idx = region_codes.index(current_region)

selected_name = st.selectbox(
    "🌍 Select Grid Region",
    region_names,
    index=current_idx,
    key="scheduler_region",
)
zone_code = regions[selected_name]
st.session_state.selected_region = zone_code

st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# ===== CURRENT CARBON INTENSITY =====
carbon_data = get_carbon_intensity(zone_code)
ci = carbon_data["carbon_intensity"]
is_mock = carbon_data["is_mock"]
status_label, status_color = get_grid_status(ci)

gauge_col, status_col = st.columns([2, 1])

with gauge_col:
    st.markdown("### ⚡ Current Carbon Intensity")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ci,
        number=dict(suffix=" gCO₂/kWh", font=dict(size=24, color="#E6EDF3")),
        title=dict(text=f"{selected_name}", font=dict(size=14, color="#8B949E")),
        gauge=dict(
            axis=dict(range=[0, 700], tickcolor="#8B949E", tickfont=dict(color="#8B949E")),
            bar=dict(color="#58A6FF", thickness=0.3),
            bgcolor="#1C2128",
            borderwidth=0,
            steps=[
                dict(range=[0, 100], color="rgba(0,255,136,0.2)"),
                dict(range=[100, 250], color="rgba(240,165,0,0.2)"),
                dict(range=[250, 700], color="rgba(255,75,75,0.2)"),
            ],
            threshold=dict(
                line=dict(color="#FFFFFF", width=3),
                thickness=0.75,
                value=ci,
            ),
        ),
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(l=30, r=30, t=50, b=10),
    )
    st.plotly_chart(fig, width="stretch")

with status_col:
    st.markdown("### 📊 Grid Status")
    
    dot_class = "live-dot"
    color_hex = "#00FF88"
    if status_color == "red":
        dot_class = "live-dot live-dot-red"
        color_hex = "#FF4B4B"
    elif status_color == "orange":
        dot_class = "live-dot live-dot-yellow"
        color_hex = "#F0A500"
    
    mock_label = " (mock data)" if is_mock else ""
    renewable_pct = max(0, 100 - ci / 7)
    
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size:1.4rem;font-weight:700;color:{color_hex};margin-bottom:8px;">
            <span class="{dot_class}"></span> {status_label}
        </div>
        <div style="color:#E6EDF3;font-size:0.95rem;margin-bottom:12px;">
            {ci:.0f} gCO₂/kWh{mock_label}
        </div>
        <div style="color:#8B949E;font-size:0.85rem;">
            ~{renewable_pct:.0f}% renewable energy estimated
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Status explanation
    if ci < 100:
        st.success("✅ NOW is a great time to run your workloads. Grid is clean!")
    elif ci < 250:
        st.warning("⚠️ Mixed grid. Consider scheduling heavy workloads for a greener window.")
    else:
        st.error("🚨 High carbon grid. Delay heavy workloads if possible.")

st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# ===== 24-HOUR FORECAST =====
st.markdown("### 📈 24-Hour Carbon Intensity Forecast")

forecast = get_carbon_forecast(zone_code)
best_window = get_best_window(forecast)

# Build forecast chart
df = pd.DataFrame(forecast)
hours = list(range(len(df)))
tick_labels = [t[-5:] for t in df["timestamp"]]  # Show HH:MM

fig2 = go.Figure()

# Main line
fig2.add_trace(go.Scatter(
    x=hours,
    y=df["carbon_intensity"],
    mode="lines+markers",
    line=dict(color="#58A6FF", width=2.5),
    marker=dict(size=5, color="#58A6FF"),
    fill="tozeroy",
    fillcolor="rgba(88,166,255,0.06)",
    name="Carbon Intensity",
))

# NOW marker — vertical line shape
fig2.add_shape(
    type="line", x0=0, x1=0, y0=0, y1=1,
    yref="paper", line=dict(color="#00FF88", width=2, dash="dash"),
)

# Best window highlight
best_start = best_window["best_start_hour"]
best_end = min(best_start + 3, len(df) - 1)
if best_start < len(df) and best_end < len(df):
    fig2.add_shape(
        type="rect", x0=best_start, x1=best_end, y0=0, y1=1,
        yref="paper",
        fillcolor="rgba(0,255,136,0.12)",
        line=dict(color="#00FF88", width=1, dash="dot"),
    )

# Threshold lines
fig2.add_hline(y=100, line_dash="dot", line_color="rgba(0,255,136,0.3)", line_width=1)
fig2.add_hline(y=250, line_dash="dot", line_color="rgba(255,75,75,0.3)", line_width=1)

# Annotations (added separately to avoid Plotly 6.x bug)
annotations = [
    dict(x=0, y=1, yref="paper", text="NOW", showarrow=False,
         font=dict(color="#00FF88", size=12), yanchor="bottom"),
]
if best_start < len(df):
    annotations.append(
        dict(x=best_start, y=1, yref="paper", text="BEST WINDOW", showarrow=False,
             font=dict(color="#00FF88", size=11), yanchor="bottom")
    )

fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        title="Time", showgrid=False, color="#8B949E",
        tickangle=-45,
        tickvals=hours[::2],
        ticktext=tick_labels[::2],
    ),
    yaxis=dict(
        title="gCO₂/kWh", showgrid=True,
        gridcolor="#30363D", color="#8B949E",
    ),
    height=380,
    margin=dict(l=40, r=20, t=30, b=60),
    showlegend=False,
    annotations=annotations,
)
st.plotly_chart(fig2, width="stretch")

# ===== SCHEDULING RECOMMENDATION =====
st.markdown("### 🗓️ Scheduling Recommendation")

rec_col1, rec_col2 = st.columns(2)

with rec_col1:
    best_avg = best_window["best_avg_intensity"]
    savings_pct = best_window["savings_percent"]
    
    if ci < 100:
        st.markdown(f'''
        <div class="energy-callout">
            <div class="callout-value" style="font-size:1.5rem;">✅ Run Now!</div>
            <div class="callout-label">Grid is clean at {ci:.0f} gCO₂/kWh. Great time to run workloads.</div>
        </div>
        ''', unsafe_allow_html=True)
    elif ci < 250:
        hours_to_wait = best_start if best_start > 0 else 1
        st.markdown(f'''
        <div class="metric-card" style="border-left-color:#F0A500;">
            <div class="metric-label">⚠️ CONSIDER WAITING</div>
            <div class="metric-value" style="font-size:1.2rem;color:#F0A500;">
                Best window in ~{hours_to_wait}h
            </div>
            <div class="metric-delta" style="color:#8B949E;">
                Intensity drops to {best_avg:.0f} gCO₂/kWh ({savings_pct:.1f}% savings)
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        hours_to_wait = best_start if best_start > 0 else 2
        st.markdown(f'''
        <div class="danger-callout">
            <div class="callout-value" style="color:#FF4B4B;font-size:1.5rem;">
                🚨 Delay by {hours_to_wait}h
            </div>
            <div class="callout-label" style="color:#FF4B4B;">
                High carbon grid ({ci:.0f} gCO₂/kWh). Wait for {best_avg:.0f} gCO₂/kWh ({savings_pct:.1f}% reduction).
            </div>
        </div>
        ''', unsafe_allow_html=True)

with rec_col2:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-label">OPTIMAL WINDOW</div>
        <div class="metric-value" style="font-size:1.2rem;">
            In {best_start} hours
        </div>
        <div style="color:#8B949E;font-size:0.85rem;margin-top:8px;">
            Best 3-hour avg: {best_avg:.0f} gCO₂/kWh<br/>
            Current: {ci:.0f} gCO₂/kWh<br/>
            Potential savings: {savings_pct:.1f}%
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# ===== WORKLOAD CARBON CALCULATOR =====
st.markdown("### 🧮 Carbon Cost Calculator")

calc_col1, calc_col2 = st.columns(2)

with calc_col1:
    joules_input = st.number_input(
        "Enter your workload energy (Joules)",
        min_value=0.0,
        max_value=1000.0,
        value=5.0,
        step=0.5,
        key="carbon_calc_joules",
    )

with calc_col2:
    if joules_input > 0:
        kwh = joules_input / 3600 / 1000
        co2_now = kwh * ci
        co2_best = kwh * best_avg
        savings_g = co2_now - co2_best
        
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">CARBON COMPARISON</div>
            <div style="display:flex;justify-content:space-between;margin-top:8px;">
                <div style="text-align:center;">
                    <div style="color:#FF4B4B;font-family:'JetBrains Mono';font-weight:700;">
                        {format_co2(co2_now)}
                    </div>
                    <div style="color:#8B949E;font-size:0.8rem;">Run Now</div>
                </div>
                <div style="text-align:center;color:#00FF88;font-size:1.5rem;">→</div>
                <div style="text-align:center;">
                    <div style="color:#00FF88;font-family:'JetBrains Mono';font-weight:700;">
                        {format_co2(co2_best)}
                    </div>
                    <div style="color:#8B949E;font-size:0.8rem;">Best Window</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if savings_g > 0:
            equivalents = get_emissions_equivalents(savings_g)
            st.markdown(f"**By waiting {best_start}h, you save {format_co2(savings_g)}:**")
            for eq in equivalents[:3]:
                st.markdown(f"&nbsp;&nbsp;{eq}")

# Footer
st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Making Every Joule Count ⚡</div>',
    unsafe_allow_html=True,
)
