"""
JouleLens — AI Green Refactor Page.
AI-powered code optimization suggestions using Claude.
"""

import streamlit as st
import difflib
import json

from styles import CSS
from ai_refactor import get_green_refactor
from database import update_run_with_refactor, init_db
from utils import score_to_color, score_to_label, score_to_css_class, DEMO_SNIPPETS

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Ensure DB is initialized
init_db()

# Header
st.markdown('<h1 class="gradient-header">🤖 AI Green Refactor</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="gradient-subtitle">Claude-powered energy optimization for your Python code</p>',
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
code = st.text_area(
    "📄 Code to Refactor",
    value=code,
    height=250,
    key="refactor_code_input",
    placeholder="Paste Python code to refactor...",
)

# ===== GENERATE REFACTOR =====
st.markdown("")
refactor_clicked = st.button("🌿 Generate Green Refactor", width="stretch", type="primary")

if refactor_clicked and code.strip():
    with st.spinner("🤖 JouleLens AI is analyzing your code for energy waste..."):
        result = get_green_refactor(code, function_breakdown)
    
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
            st.caption("🔧 *Demo mode — add ANTHROPIC_API_KEY to .env for Claude-powered analysis*")
        
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
        with diff_col1:
            st.markdown("**📌 Original Code**")
            st.code(code, language="python")
        with diff_col2:
            st.markdown("**✅ Refactored Code**")
            st.code(refactored_code, language="python")
        
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
