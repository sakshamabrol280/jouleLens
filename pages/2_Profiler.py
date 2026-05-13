"""
JouleLens — Code Profiler Page.
Core feature: submit code, see energy breakdown.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import time
from datetime import datetime

from styles import CSS
from database import insert_run, init_db
from energy_simulator import (
    simulate_energy, calculate_cost_and_carbon,
    calculate_joule_score, get_emissions_equivalents,
)
from carbon_api import get_carbon_intensity
from utils import (
    format_joules, format_currency, format_co2,
    score_to_color, score_to_label, score_to_css_class,
    DEMO_SNIPPETS, analyze_complexity,
)

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Ensure DB is initialized
init_db()

# Header
st.markdown('<h1 class="gradient-header">⚡ Code Profiler</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">Measure the energy cost of every function in your code</p>',
    unsafe_allow_html=True,
)

# ===== DEMO SNIPPETS =====
st.markdown("#### 📝 Quick Load Demo Snippets")
demo_cols = st.columns(len(DEMO_SNIPPETS))
demo_keys = list(DEMO_SNIPPETS.keys())
button_labels = ["Demo 1", "Demo 2", "Demo 3"]

for i, name in enumerate(demo_keys):
    with demo_cols[i]:
        label = button_labels[i] if i < len(button_labels) else name
        if st.button(label, key=f"demo_{i}", width="stretch"):
            # Update the text area directly using its key for instant UI update
            st.session_state.code_input = DEMO_SNIPPETS[name]
            st.session_state.current_code = DEMO_SNIPPETS[name]

st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# ===== CODE INPUT =====
col_input, col_opts = st.columns([3, 1])

with col_input:
    # Use code_input from session state if it exists, otherwise use current_code
    initial_value = st.session_state.get("code_input", st.session_state.get("current_code", ""))
    
    code = st.text_area(
        "📄 Write Code",
        value=initial_value,
        height=300,
        key="code_input",
        placeholder="# Paste your Python code here...\ndef my_function():\n    pass",
    )
    st.session_state.current_code = code

with col_opts:
    st.markdown("#### ⚙️ Options")
    
    # File uploader
    uploaded = st.file_uploader("📁 Or upload a .py file", type=["py"])
    if uploaded is not None:
        file_content = uploaded.read().decode("utf-8")
        st.session_state.current_code = file_content
        st.rerun()
    
    # Workload type
    workload_type = st.radio(
        "🔧 Workload Type",
        ["CPU-Bound", "Memory-Bound", "I/O-Bound"],
        index=0,
        key="workload_type",
    )

# ===== PROFILE BUTTON =====
st.markdown("")
profile_clicked = st.button("⚡ Profile Energy", width="stretch", type="primary")

if profile_clicked and st.session_state.current_code.strip():
    # Animated progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        (0.15, "🔍 Parsing AST..."),
        (0.30, "🔧 Instrumenting functions..."),
        (0.50, "📊 Reading CPU telemetry..."),
        (0.70, "💾 Calculating DRAM cost..."),
        (0.85, "🏆 Scoring efficiency..."),
    ]
    
    for progress, msg in steps:
        progress_bar.progress(progress)
        status_text.markdown(f"**{msg}**")
        time.sleep(0.4)
    
    # Run simulation
    result = simulate_energy(st.session_state.current_code, workload_type)
    
    if "error" in result and result.get("total_joules", 0) == 0:
        progress_bar.progress(1.0)
        status_text.empty()
        st.error(f"❌ Code execution error: {result['error']}")
    else:
        # Calculate cost and carbon
        region = st.session_state.get("selected_region", "US-CAL-CISO")
        carbon_data = get_carbon_intensity(region)
        ci = carbon_data["carbon_intensity"]
        cost_per_kwh = st.session_state.get("cost_per_kwh", 0.12)
        
        cost_carbon = calculate_cost_and_carbon(
            result["total_joules"], cost_per_kwh, ci
        )
        
        score = calculate_joule_score(result["total_joules"])
        
        # Save to DB
        run_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code_snippet": st.session_state.current_code,
            "workload_type": workload_type,
            "total_joules": result["total_joules"],
            "total_wh": cost_carbon["wh"],
            "cost_usd": cost_carbon["cost_usd"],
            "co2_grams": cost_carbon["co2_grams"],
            "joule_score": score,
            "region": region,
            "carbon_intensity": ci,
            "function_breakdown": result["function_breakdown"],
        }
        run_id = insert_run(run_data)
        
        # Store in session state for refactor page
        st.session_state.last_profiling_result = result
        st.session_state.last_run_id = run_id
        st.session_state.last_score = score
        st.session_state.last_cost_carbon = cost_carbon
        
        progress_bar.progress(1.0)
        status_text.markdown("**✅ Profiling complete!**")
        time.sleep(0.3)
        status_text.empty()
        progress_bar.empty()
        
        # ===== RESULTS =====
        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 📊 Profiling Results")
        
        # Score badge
        css_class = score_to_css_class(score)
        label = score_to_label(score)
        st.markdown(
            f'<div style="text-align:center;margin:1rem 0;">'
            f'<span class="score-badge {css_class}">Joule Score: {score} — {label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Metric columns
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("⚡ Total Energy", format_joules(result["total_joules"]))
        with m2:
            st.metric("🔋 Watt-hours", f"{cost_carbon['wh']:.6f} Wh")
        with m3:
            st.metric("💰 Estimated Cost", format_currency(cost_carbon["cost_usd"]))
        with m4:
            st.metric("🌿 CO₂ Emitted", format_co2(cost_carbon["co2_grams"]))
        
        # Execution time & Complexity
        time_c, space_c = analyze_complexity(st.session_state.current_code)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="energy-callout">'
                f'<div class="callout-value">{result["execution_time_ms"]:.1f} ms</div>'
                f'<div class="callout-label">Execution Time</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="energy-callout">'
                f'<div class="callout-value" style="color:var(--accent-blue);">{time_c}</div>'
                f'<div class="callout-label">Est. Time Complexity</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="energy-callout">'
                f'<div class="callout-value" style="color:var(--accent-warning);">{space_c}</div>'
                f'<div class="callout-label">Est. Space Complexity</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        
        # Function breakdown table
        st.markdown("### 🔬 Function Energy Breakdown")
        fb = result["function_breakdown"]
        if fb:
            df = pd.DataFrame(fb)
            df = df.rename(columns={
                "function_name": "Function",
                "calls": "Calls",
                "time_ms": "Time (ms)",
                "joules": "Joules",
                "percent_of_total": "% Total",
                "grade": "Grade",
            })
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Joules": st.column_config.NumberColumn(format="%.4f"),
                    "Time (ms)": st.column_config.NumberColumn(format="%.2f"),
                    "% Total": st.column_config.NumberColumn(format="%.1f%%"),
                },
            )
        
        # Bar chart
        if fb and len(fb) > 1:
            st.markdown("### 📊 Energy per Function")
            fig = go.Figure()
            
            sorted_fb = sorted(fb, key=lambda x: x["joules"])
            names = [f["function_name"] for f in sorted_fb]
            joules_vals = [f["joules"] for f in sorted_fb]
            colors_bar = [score_to_color(f["grade"]) for f in sorted_fb]
            
            fig.add_trace(go.Bar(
                y=names, x=joules_vals,
                orientation="h",
                marker=dict(color=colors_bar, line=dict(width=0)),
                text=[f"{j:.4f} J" for j in joules_vals],
                textposition="outside",
                textfont=dict(color="#E6EDF3", size=11),
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="Joules", showgrid=True, gridcolor="#30363D", color="#8B949E"),
                yaxis=dict(showgrid=False, color="#E6EDF3"),
                height=max(200, len(fb) * 45),
                margin=dict(l=10, r=80, t=10, b=30),
                showlegend=False,
            )
            st.plotly_chart(fig, width="stretch")
        
        # Emissions equivalents
        st.markdown("### 🌍 Emissions Equivalent")
        equivalents = get_emissions_equivalents(cost_carbon["co2_grams"])
        eq_cols = st.columns(len(equivalents))
        for i, eq in enumerate(equivalents):
            with eq_cols[i]:
                st.markdown(
                    f'<div class="metric-card" style="text-align:center;padding:12px;">'
                    f'<div style="font-size:0.85rem;color:#E6EDF3;">{eq}</div></div>',
                    unsafe_allow_html=True,
                )
        
        # AI Refactor button
        st.markdown("")
        if st.button("🤖 Get AI Green Refactor →", width="stretch"):
            st.switch_page("pages/3_Refactor.py")

elif profile_clicked:
    st.warning("⚠️ Please paste some code to profile.")

# Footer
st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Making Every Joule Count ⚡</div>',
    unsafe_allow_html=True,
)
