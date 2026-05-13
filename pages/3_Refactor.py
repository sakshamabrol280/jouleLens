"""
JouleLens — AI Green Refactor Page.
AI-powered code optimization suggestions using Gemini.
"""

import streamlit as st
import difflib
import json

from styles import CSS
from ai_refactor import get_green_refactor
from database import update_run_with_refactor, init_db
from utils import score_to_color, score_to_label, score_to_css_class, DEMO_SNIPPETS, format_joules

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Ensure DB is initialized
init_db()

# Header
st.markdown('<h1 class="gradient-header">🤖 AI Green Refactor</h1>', unsafe_allow_html=True)
language = st.session_state.get("selected_language", "Python")

st.markdown(
    f'<p class="gradient-subtitle">Gemini-powered energy optimization for your {language} code</p>',
    unsafe_allow_html=True,
)

# ===== CODE INPUT =====
last_result = st.session_state.get("last_profiling_result", None)
code = st.session_state.get("current_code", "")
function_breakdown = None

if last_result and code:
    function_breakdown = last_result.get("function_breakdown", [])
    
    # Show high-Joule function warnings
    if function_breakdown:
        sorted_funcs = sorted(function_breakdown, key=lambda x: x.get("joules", 0), reverse=True)[:3]
        st.markdown("### ⚠️ High-Energy Functions Detected")
        for f in sorted_funcs:
            if f["joules"] > 0.001:
                st.warning(
                    f"**{f['function_name']}** — {f['joules']:.4f} J "
                    f"({f['percent_of_total']:.1f}% of total) | "
                    f"Grade: {f['grade']} | Called {f['calls']}x"
                )
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

# Manual code input if not from profiler
col_lang, col_space = st.columns([1, 3])
with col_lang:
    current_lang = st.session_state.get("selected_language", "Python")
    language = st.selectbox(
        "🌐 Language",
        ["Python", "C", "C++", "Java"],
        index=["Python", "C", "C++", "Java"].index(current_lang) if current_lang in ["Python", "C", "C++", "Java"] else 0,
        key="refactor_language_selector"
    )

code = st.text_area(
    "📄 Code to Refactor",
    value=code,
    height=250,
    key="refactor_code_input",
    placeholder=f"Paste {language} code to refactor...",
)

# ===== GENERATE REFACTOR =====
st.markdown("")
refactor_clicked = st.button("🌿 Generate Green Refactor", width="stretch", type="primary")

if refactor_clicked and code.strip():
    with st.spinner("🤖 JouleLens AI is analyzing your code for energy waste..."):
        result = get_green_refactor(code, function_breakdown, language)
        
        # If the user didn't run the Profiler first, run it now in the background
        if not last_result or "p_idle" not in last_result:
            from energy_simulator import simulate_energy
            last_result = simulate_energy(code, workload_type="CPU-Bound", language=language)
    
    if "error" in result:
        st.error(f"❌ {result['error']}")
    else:
        st.session_state.last_refactor_result = result
        
        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 🌿 Refactoring Results")
        
        # Summary
        summary = result.get("summary", "No summary available.")
        st.info(f"💡 **Analysis Summary:** {summary}")
        
        # Mock mode indicator
        if result.get("_mock"):
            st.caption("🔧 *Demo mode — add GEMINI_API_KEY to .env for Gemini-powered analysis*")
        
        # Before/After score badges
        score_before = result.get("green_score_before", "D")
        score_after = result.get("green_score_after", "B")
        
        s1, s2, s3 = st.columns([2, 1, 2])
        with s1:
            css_b = score_to_css_class(score_before)
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="color:#8B949E;margin-bottom:8px;">BEFORE</div>'
                f'<span class="score-badge {css_b}">{score_before} — {score_to_label(score_before)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                '<div style="text-align:center;font-size:2.5rem;padding-top:20px;color:#00FF88;">→</div>',
                unsafe_allow_html=True,
            )
        with s3:
            css_a = score_to_css_class(score_after)
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="color:#8B949E;margin-bottom:8px;">AFTER</div>'
                f'<span class="score-badge {css_a}">{score_after} — {score_to_label(score_after)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        
        # Energy reduction callout
        reduction = result.get("estimated_energy_reduction_percent", 0)
        
        if last_result and "p_idle" in last_result:
            old_p_idle = last_result.get("p_idle", 0)
            old_p_total = last_result.get("p_total", 0)
            old_e_net = last_result.get("total_joules", 0)
            
            new_e_net = old_e_net * (1 - reduction/100.0)
            est_p_total = old_p_idle + (old_p_total - old_p_idle) * (1 - reduction/100.0)
            
            st.markdown("### 📉 Projected Differential Baseline")
            db1, db2, db3 = st.columns(3)
            with db1:
                st.metric("System Idle Baseline (P_idle)", f"{old_p_idle:.2f} W", "No Change", delta_color="off")
            with db2:
                st.metric("Est. New Peak Power (P_total)", f"{est_p_total:.2f} W", f"-{reduction}%")
            with db3:
                st.metric("Projected Net Energy (E_net)", format_joules(new_e_net), f"-{format_joules(old_e_net - new_e_net)}")
                
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="energy-callout">'
                f'<div class="callout-value">-{reduction}%</div>'
                f'<div class="callout-label">Estimated Energy Reduction</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        
        # Side-by-side diff view
        st.markdown("### 📝 Code Comparison")
        refactored_code = result.get("refactored_code", "")
        
        diff_col1, diff_col2 = st.columns(2)
        lang_str = "python" if language == "Python" else ("cpp" if language == "C++" else ("c" if language == "C" else "java"))
        with diff_col1:
            st.markdown("**📌 Original Code**")
            st.code(code, language=lang_str)
        with diff_col2:
            st.markdown("**✅ Refactored Code**")
            st.code(refactored_code, language=lang_str)
        
        # Unified diff
        with st.expander("📋 View Unified Diff"):
            diff = difflib.unified_diff(
                code.splitlines(keepends=True),
                refactored_code.splitlines(keepends=True),
                fromfile="original.py",
                tofile="refactored.py",
            )
            diff_text = "".join(diff)
            if diff_text:
                st.code(diff_text, language="diff")
            else:
                st.info("No differences detected.")
        
        # Optimization cards
        optimizations = result.get("optimizations", [])
        if optimizations:
            st.markdown("### 🛠️ Optimizations Applied")
            for opt in optimizations:
                title = opt.get("title", "Optimization")
                desc = opt.get("description", "")
                technique = opt.get("technique", "other")
                impact = opt.get("impact", "medium")
                
                impact_class = f"impact-{impact}"
                
                with st.expander(f"💡 {title}", expanded=True):
                    st.markdown(f"{desc}")
                    st.markdown(
                        f'<span class="technique-badge">{technique}</span>'
                        f'<span class="technique-badge {impact_class}">{impact} impact</span>',
                        unsafe_allow_html=True,
                    )
        
        # Save to history
        st.markdown("")
        save_col, copy_col = st.columns(2)
        with save_col:
            run_id = st.session_state.get("last_run_id")
            if run_id and st.button("💾 Save Refactor to History", width="stretch"):
                update_run_with_refactor(
                    run_id,
                    summary,
                    refactored_code,
                    reduction,
                )
                st.success("✅ Refactor saved to history!")
        
        with copy_col:
            st.markdown("**📋 Copy refactored code from above**")

elif refactor_clicked:
    st.warning("⚠️ Please paste some code to refactor.")

# Footer
st.markdown(
    '<div class="joulelens-footer">Powered by JouleLens AI — Making Every Joule Count ⚡</div>',
    unsafe_allow_html=True,
)
