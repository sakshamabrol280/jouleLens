"""
JouleLens — History & Reports Page.
Log of all profiling runs with export capability.
"""

import streamlit as st
import pandas as pd
import json

from styles import CSS
from database import get_all_runs, clear_all_runs, get_run_by_id, init_db
from report_generator import generate_pdf_report, generate_json_report
from utils import (
    format_joules, format_currency, format_co2,
    score_to_color, score_to_label, truncate_code,
)

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Ensure DB is initialized
init_db()

# Header
st.markdown('<h1 class="gradient-header">📊 History & Reports</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">Complete log of all profiling runs with export capability</p>',
    unsafe_allow_html=True,
)

# Fetch all runs
runs = get_all_runs()

if not runs:
    st.info("📭 No profiling runs yet. Head to the Profiler to create your first run!")
else:
    # ===== SUMMARY STATS =====
    total_runs = len(runs)
    total_joules = sum(r.get("total_joules", 0) for r in runs)
    total_co2 = sum(r.get("co2_grams", 0) for r in runs)
    total_cost = sum(r.get("cost_usd", 0) for r in runs)
    
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("🔬 Total Runs", str(total_runs))
    with s2:
        st.metric("⚡ Total Energy", format_joules(total_joules))
    with s3:
        st.metric("🌿 Total CO₂", format_co2(total_co2))
    with s4:
        st.metric("💰 Total Cost", format_currency(total_cost))
    
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    
    # ===== DATA TABLE =====
    st.markdown("### 📋 All Profiling Runs")
    
    table_data = []
    for r in runs:
        table_data.append({
            "Run ID": r["id"],
            "Timestamp": r.get("timestamp", "N/A"),
            "Code": truncate_code(r.get("code_snippet", ""), 60),
            "Joules": round(r.get("total_joules", 0), 4),
            "Wh": f"{r.get('total_wh', 0):.6f}",
            "Cost (₹)": f"₹{r.get('cost_usd', 0):.6f}",
            "CO₂ (g)": round(r.get("co2_grams", 0), 4),
            "Score": r.get("joule_score", "?"),
            "Region": r.get("region", "N/A"),
            "AI Refactored": "✅" if r.get("ai_refactor_available") else "—",
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Run ID": st.column_config.NumberColumn(width="small"),
            "Joules": st.column_config.NumberColumn(format="%.4f"),
            "Score": st.column_config.TextColumn(width="small"),
        },
    )
    
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    
    # ===== DETAILED RUN EXPANDERS =====
    st.markdown("### 📄 Run Details")
    
    for r in runs:
        run_id = r["id"]
        score = r.get("joule_score", "?")
        timestamp = r.get("timestamp", "N/A")
        color = score_to_color(score)
        
        with st.expander(f"Run #{run_id} — {timestamp} — Score: {score} {score_to_label(score)}"):
            # Code
            st.markdown("**📝 Code:**")
            code_snippet = r.get("code_snippet", "")
            st.code(code_snippet[:800] if len(code_snippet) > 800 else code_snippet, language="python")
            
            # Metrics
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                st.metric("Energy", format_joules(r.get("total_joules", 0)))
            with mc2:
                st.metric("Cost", format_currency(r.get("cost_usd", 0)))
            with mc3:
                st.metric("CO₂", format_co2(r.get("co2_grams", 0)))
            with mc4:
                st.metric("Region", r.get("region", "N/A"))
            
            # Function breakdown
            fb_raw = r.get("function_breakdown", "[]")
            if isinstance(fb_raw, str):
                try:
                    fb = json.loads(fb_raw)
                except json.JSONDecodeError:
                    fb = []
            else:
                fb = fb_raw
            
            if fb:
                st.markdown("**🔬 Function Breakdown:**")
                fb_df = pd.DataFrame(fb)
                st.dataframe(fb_df, width="stretch", hide_index=True)
            
            # AI refactor
            if r.get("ai_refactor_available"):
                st.markdown("**🤖 AI Refactor Summary:**")
                st.info(r.get("ai_summary", "No summary available."))
                reduction = r.get("ai_energy_reduction_percent")
                if reduction:
                    st.markdown(f"**Estimated Energy Reduction:** -{reduction}%")
            
            # Export buttons
            st.markdown("**📥 Export:**")
            exp1, exp2 = st.columns(2)
            with exp1:
                pdf_buffer = generate_pdf_report(r)
                st.download_button(
                    "📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"joulelens_run_{run_id}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{run_id}",
                )
            with exp2:
                json_str = generate_json_report(r)
                st.download_button(
                    "📥 Download JSON",
                    data=json_str,
                    file_name=f"joulelens_run_{run_id}.json",
                    mime="application/json",
                    key=f"json_{run_id}",
                )
    
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    
    # ===== CLEAR HISTORY =====
    st.markdown("### 🗑️ Manage History")
    
    if not st.session_state.get("confirm_clear", False):
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state.confirm_clear = True
            st.rerun()
    else:
        st.warning("⚠️ Are you sure? This will delete ALL profiling runs permanently.")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✅ Yes, Clear Everything", type="primary"):
                clear_all_runs()
                st.session_state.confirm_clear = False
                st.success("✅ All history cleared.")
                st.rerun()
        with cc2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_clear = False
                st.rerun()

# Footer
st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Making Every Joule Count ⚡</div>',
    unsafe_allow_html=True,
)
