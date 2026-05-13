"""
JouleLens — Energy Simulation Engine.
Simulates Intel RAPL-style CPU + DRAM Joule readings using execution time × TDP coefficients.
All readings are clearly labeled as simulated telemetry.
"""

import cProfile
import pstats
import time
import ast
import sys
import random


# TDP constants (simulated)
BASE_TDP_WATTS = 15  # Simulated laptop CPU TDP
DRAM_WATTS = 3

# Workload multipliers
WORKLOAD_MULTIPLIERS = {
    "CPU-Bound": 1.4,
    "Memory-Bound": 1.1,
    "I/O-Bound": 0.7,
}

# Pre-define allowed built-in modules for O(1) memory-efficient lookup
ALLOWED_BUILTINS = frozenset({"<module>", "<listcomp>", "<dictcomp>", "<genexpr>"})


def simulate_energy(code_string, workload_type="CPU-Bound"):
    """
    Profile a Python code string and return simulated energy measurements.
    
    Returns dict with total_joules, cpu_joules, dram_joules, total_wh,
    execution_time_ms, and function_breakdown list.
    """
    multiplier = WORKLOAD_MULTIPLIERS.get(workload_type, 1.0)

    # Parse AST to find function names efficiently
    try:
        tree = ast.parse(code_string)
        defined_functions = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
    except SyntaxError:
        defined_functions = []

    exec_ns = {"__builtins__": __builtins__}
    profiler = None
    profiler_stats = None
    
    # Deterministically check if a profiler is already active to prevent RuntimeError
    can_profile = sys.getprofile() is None

    try:
        if can_profile:
            profiler = cProfile.Profile()
            start_time = time.perf_counter()
            profiler.enable()
            exec(code_string, exec_ns)
            profiler.disable()
            end_time = time.perf_counter()
            
            # Avoid io.StringIO() allocation and redundant sort_stats() overhead
            profiler_stats = pstats.Stats(profiler)
        else:
            start_time = time.perf_counter()
            exec(code_string, exec_ns)
            end_time = time.perf_counter()
            
    except Exception as e:
        if profiler is not None:
            try:
                profiler.disable()
            except Exception:
                pass
        return {
            "error": str(e),
            "total_joules": 0, "cpu_joules": 0, "dram_joules": 0,
            "total_wh": 0, "execution_time_ms": 0,
            "function_breakdown": [],
        }

    total_time = max(0.0, end_time - start_time)

    # Calculate energy using standard library random instead of heavy numpy
    cpu_joules = BASE_TDP_WATTS * total_time * multiplier
    dram_joules = DRAM_WATTS * total_time * 0.3
    noise = random.gauss(0, 0.05 * cpu_joules) if cpu_joules > 0 else 0
    total_joules = max(0.001, cpu_joules + dram_joules + noise)

    function_breakdown = []

    if profiler_stats is not None:
        # Direct access to .stats dict without stream formatting
        for (_, _, name), (_, nc, _, ct, _) in profiler_stats.stats.items():
            if ct <= 0:
                continue
            
            # Optimized string matching and set lookup
            if name and name[0] == "<" and name not in ALLOWED_BUILTINS:
                continue

            time_fraction = ct / total_time if total_time > 0 else 0
            func_joules = total_joules * time_fraction

            function_breakdown.append({
                "function_name": name,
                "calls": nc,
                "time_ms": round(ct * 1000, 3),
                "joules": round(func_joules, 6),
                "percent_of_total": round(time_fraction * 100, 2),
                "grade": _grade_joules(func_joules),
            })

    # Sort manually only once
    function_breakdown.sort(key=lambda x: x["joules"], reverse=True)
    function_breakdown = function_breakdown[:20]

    if not function_breakdown:
        if defined_functions:
            # Hoist calculations out of the loop
            num_funcs = len(defined_functions)
            per_func_joules = total_joules / num_funcs
            per_func_time = total_time / num_funcs
            percent = 100.0 / num_funcs
            grade = _grade_joules(per_func_joules)
            
            # Limit to 20 to match profiler behavior and prevent memory runaway
            for fn in defined_functions[:20]:
                function_breakdown.append({
                    "function_name": fn,
                    "calls": 1,
                    "time_ms": round(per_func_time * 1000, 3),
                    "joules": round(per_func_joules, 6),
                    "percent_of_total": round(percent, 2),
                    "grade": grade,
                })
        else:
            function_breakdown = [{
                "function_name": "<module>",
                "calls": 1,
                "time_ms": round(total_time * 1000, 3),
                "joules": round(total_joules, 6),
                "percent_of_total": 100.0,
                "grade": _grade_joules(total_joules),
            }]

    return {
        "total_joules": round(total_joules, 6),
        "cpu_joules": round(cpu_joules, 6),
        "dram_joules": round(dram_joules, 6),
        "total_wh": round(total_joules / 3600, 8),
        "execution_time_ms": round(total_time * 1000, 3),
        "function_breakdown": function_breakdown,
    }


def _grade_joules(joules):
    """Grade a function's energy consumption A-F."""
    if joules < 0.1:
        return "A"
    elif joules < 0.5:
        return "B"
    elif joules < 2.0:
        return "C"
    elif joules < 10.0:
        return "D"
    else:
        return "F"


def calculate_cost_and_carbon(joules, cost_per_kwh=0.12, carbon_intensity_gco2_per_kwh=300):
    """Convert Joules to Wh, kWh, USD cost, and gCO₂ emitted."""
    kwh = joules / 3600000.0
    return {
        "wh": round(joules / 3600.0, 8),
        "kwh": round(kwh, 10),
        "cost_usd": round(kwh * cost_per_kwh, 8),
        "co2_grams": round(kwh * carbon_intensity_gco2_per_kwh, 6),
    }


def calculate_joule_score(total_joules):
    """Calculate overall Joule Score (A-F) based on total energy."""
    if total_joules < 1:
        return "A"
    elif total_joules < 5:
        return "B"
    elif total_joules < 15:
        return "C"
    elif total_joules < 30:
        return "D"
    else:
        return "F"


def get_emissions_equivalents(co2_grams):
    """Convert CO₂ grams to human-relatable equivalents."""
    if co2_grams <= 0:
        return ["⚡ Negligible carbon footprint"]
    return [
        f"🚗 = {co2_grams / 404:.4f} miles driven (avg car)",
        f"📱 = {co2_grams / 0.06:.1f} smartphone charges",
        f"🛍️ = {co2_grams / 10:.3f} plastic bags produced",
        f"💡 = {co2_grams / 0.4:.2f} seconds of LED bulb use"
    ]
