"""
JouleLens — AI Green Refactor Engine.
Uses Google Gemini API to suggest energy-efficient code refactors.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_system_prompt(language):
    return f"""You are JouleLens AI, an expert in energy-efficient {language} programming. 
You analyze code for energy waste and suggest optimizations that reduce CPU cycles, 
memory allocations, and unnecessary computation. You think in Joules, not just milliseconds.

When given {language} code, you must respond with valid JSON only, in this exact structure:
{{
  "summary": "2-3 sentence explanation of the main energy problems found",
  "estimated_energy_reduction_percent": <integer 5-60>,
  "refactored_code": "<full refactored {language} code as a string>",
  "optimizations": [
    {{
      "title": "Optimization name",
      "description": "What was changed and why it saves energy",
      "technique": "vectorization|memoization|algorithm|io_batching|memory|other",
      "impact": "high|medium|low"
    }}
  ],
  "green_score_before": "<A|B|C|D|F>",
  "green_score_after": "<A|B|C|D|F>"
}}

IMPORTANT: Return ONLY the JSON object. No markdown, no code fences, no explanation outside the JSON."""


def get_green_refactor(code_string, function_breakdown=None, language="Python"):
    """
    Send code to Gemini for energy-optimized refactoring.
    
    Args:
        code_string: The code to refactor
        function_breakdown: List of dicts with function energy data
    
    Returns:
        Parsed JSON dict with refactoring suggestions, or {"error": str} on failure.
    """
    # Force reload environment variables to catch .env changes without restart
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    if not api_key:
        return _generate_mock_refactor(code_string)
    
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        
        # Build context about high-energy functions
        func_context = ""
        if function_breakdown:
            # Sort by joules descending, take top 3
            sorted_funcs = sorted(function_breakdown, key=lambda x: x.get("joules", 0), reverse=True)[:3]
            func_context = "\n\nHighest energy-consuming functions:\n"
            for f in sorted_funcs:
                func_context += f"- {f['function_name']}: {f['joules']:.4f}J ({f['percent_of_total']:.1f}% of total), called {f['calls']} times, grade {f['grade']}\n"
        
        user_message = f"""Analyze this {language} code for energy efficiency and provide an optimized refactored version:

```{language.lower()}
{code_string}
```
{func_context}

Return your response as a valid JSON object following the exact schema specified in your system prompt."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=get_system_prompt(language),
                temperature=0.2,
                response_mime_type="application/json",
            )
        )
        
        # Extract text content
        result_text = response.text.strip()
        
        # Strip markdown code fences if present
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            result_text = "\n".join(lines)
        
        # Parse JSON
        parsed = json.loads(result_text)
        return parsed
        
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {str(e)}"}
    except Exception as e:
        return {"error": f"AI refactoring failed: {str(e)}"}


def _generate_mock_refactor(code_string):
    """
    Generate a realistic mock refactoring response using simple heuristics.
    Used when GEMINI_API_KEY is not configured so the feature still demos.
    """
    import re

    optimizations = []
    refactored = code_string

    # Detect common patterns and build optimizations
    has_for_loop = bool(re.search(r'\bfor\b.*\brange\b', code_string))
    has_append_loop = bool(re.search(r'\.append\(', code_string))
    has_nested_loop = len(re.findall(r'\bfor\b', code_string)) >= 2
    has_string_concat = bool(re.search(r"['\"].*\+.*['\"]", code_string) or
                             re.search(r'\+=\s*["\']', code_string))
    has_list_comp = bool(re.search(r'\[.*\bfor\b.*\bin\b', code_string))
    has_import_time = 'import time' in code_string
    has_range_len = bool(re.search(r'range\(len\(', code_string))

    if has_for_loop and has_append_loop:
        optimizations.append({
            "title": "Replace append-loop with list comprehension",
            "description": "List comprehensions are compiled to optimized bytecode, avoiding repeated method lookups on .append() and reducing CPU cycles by 15-30%.",
            "technique": "algorithm",
            "impact": "high"
        })
        # Simple refactor: try to convert append loops to list comp
        refactored = re.sub(
            r'(\w+)\s*=\s*\[\]\s*\n(\s*)for\s+(\w+)\s+in\s+(.*?):\s*\n\s*\1\.append\((.*?)\)',
            r'\1 = [\5 for \3 in \4]',
            refactored
        )

    if has_nested_loop:
        optimizations.append({
            "title": "Optimize nested loop with vectorized operations",
            "description": "Nested Python loops have high interpreter overhead. Using NumPy operations or itertools can reduce energy consumption by 20-45% for large datasets.",
            "technique": "vectorization",
            "impact": "high"
        })

    if has_range_len:
        optimizations.append({
            "title": "Use enumerate() instead of range(len())",
            "description": "enumerate() avoids computing len() and indexing overhead, producing cleaner and slightly more efficient iteration.",
            "technique": "algorithm",
            "impact": "low"
        })
        refactored = re.sub(r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\)',
                           r'for \1, _item in enumerate(\2)', refactored)

    if has_string_concat:
        optimizations.append({
            "title": "Replace string concatenation with join()",
            "description": "String concatenation in loops creates O(n²) memory allocations. Using ''.join() with a generator is O(n) and drastically reduces memory and CPU energy.",
            "technique": "memory",
            "impact": "medium"
        })

    if not optimizations:
        # Generic optimization if nothing specific detected
        optimizations.append({
            "title": "Use built-in functions and generators",
            "description": "Python built-in functions (sum, map, filter) are implemented in C and execute much faster than equivalent Python loops, reducing CPU energy.",
            "technique": "algorithm",
            "impact": "medium"
        })
        optimizations.append({
            "title": "Consider lazy evaluation with generators",
            "description": "Generators yield items one at a time instead of building full lists in memory, reducing peak memory usage and DRAM energy cost.",
            "technique": "memory",
            "impact": "medium"
        })

    # Calculate mock scores
    score_before = "D" if has_nested_loop else ("C" if has_for_loop else "B")
    score_after = "B" if has_nested_loop else ("A" if has_for_loop else "A")
    reduction = 35 if has_nested_loop else (25 if has_for_loop else 15)

    return {
        "summary": f"Analysis found {len(optimizations)} energy optimization(s). "
                   f"The code contains patterns that cause unnecessary CPU cycles and memory allocations. "
                   f"Applying these optimizations could reduce energy consumption by ~{reduction}%.",
        "estimated_energy_reduction_percent": reduction,
        "refactored_code": refactored,
        "optimizations": optimizations,
        "green_score_before": score_before,
        "green_score_after": score_after,
        "_mock": True,  # Flag so the UI can indicate this is a demo response
    }
