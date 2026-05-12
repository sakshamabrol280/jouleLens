"""
JouleLens — Mock Data Seeder.
Pre-populates the database with realistic demo runs.
"""

import json
import random
from datetime import datetime, timedelta
from database import insert_run


def seed_mock_data():
    """Generate 8 mock profiling runs spanning the last 7 days."""
    regions = ["US-CAL-CISO", "US-TEX-ERCO", "GB", "DE", "FR", "IN-SO", "JP-TK", "BR-S"]
    scores = ["A", "B", "B", "C", "C", "D", "F", "A"]
    joules_list = [0.8, 2.3, 3.1, 7.5, 12.4, 22.1, 42.5, 0.4]
    
    workload_types = ["CPU-Bound", "Memory-Bound", "I/O-Bound", "CPU-Bound",
                      "CPU-Bound", "Memory-Bound", "CPU-Bound", "I/O-Bound"]
    
    code_snippets = [
        "result = [fibonacci(i) for i in range(100)]",
        "data = sorted(random.sample(range(10000), 5000))",
        "matrix = [[i*j for j in range(50)] for i in range(50)]",
        "primes = find_primes(3000)",
        "result = matrix_multiply(80)",
        "data = process_large_dataset(10000)",
        "result = find_primes(8000)",
        "cached = lru_fibonacci(200)",
    ]
    
    mock_breakdowns = [
        [{"function_name": "fibonacci", "calls": 100, "time_ms": 2.1, "joules": 0.5, "percent_of_total": 62.5, "grade": "B"},
         {"function_name": "<module>", "calls": 1, "time_ms": 1.0, "joules": 0.3, "percent_of_total": 37.5, "grade": "A"}],
        [{"function_name": "sorted", "calls": 1, "time_ms": 15.2, "joules": 1.5, "percent_of_total": 65.2, "grade": "C"},
         {"function_name": "sample", "calls": 1, "time_ms": 5.0, "joules": 0.8, "percent_of_total": 34.8, "grade": "B"}],
        [{"function_name": "<listcomp>", "calls": 50, "time_ms": 20.1, "joules": 2.0, "percent_of_total": 64.5, "grade": "C"},
         {"function_name": "<module>", "calls": 1, "time_ms": 11.0, "joules": 1.1, "percent_of_total": 35.5, "grade": "C"}],
        [{"function_name": "find_primes", "calls": 1, "time_ms": 45.3, "joules": 5.5, "percent_of_total": 73.3, "grade": "D"},
         {"function_name": "<module>", "calls": 1, "time_ms": 16.5, "joules": 2.0, "percent_of_total": 26.7, "grade": "C"}],
        [{"function_name": "matrix_multiply", "calls": 1, "time_ms": 78.5, "joules": 9.0, "percent_of_total": 72.6, "grade": "D"},
         {"function_name": "<listcomp>", "calls": 80, "time_ms": 22.3, "joules": 3.4, "percent_of_total": 27.4, "grade": "C"}],
        [{"function_name": "process_large_dataset", "calls": 1, "time_ms": 130.0, "joules": 15.0, "percent_of_total": 67.9, "grade": "D"},
         {"function_name": "sort_data", "calls": 10, "time_ms": 50.2, "joules": 7.1, "percent_of_total": 32.1, "grade": "D"}],
        [{"function_name": "find_primes", "calls": 1, "time_ms": 280.5, "joules": 35.0, "percent_of_total": 82.4, "grade": "F"},
         {"function_name": "<module>", "calls": 1, "time_ms": 60.2, "joules": 7.5, "percent_of_total": 17.6, "grade": "D"}],
        [{"function_name": "fibonacci", "calls": 200, "time_ms": 0.8, "joules": 0.25, "percent_of_total": 62.5, "grade": "A"},
         {"function_name": "<module>", "calls": 1, "time_ms": 0.5, "joules": 0.15, "percent_of_total": 37.5, "grade": "A"}],
    ]
    
    carbon_intensities = [210, 380, 185, 320, 58, 620, 470, 95]
    
    now = datetime.now()
    
    for i in range(8):
        days_ago = 7 - i  # Spread across 7 days
        ts = now - timedelta(days=days_ago, hours=random.randint(0, 12))
        
        total_j = joules_list[i]
        wh = total_j / 3600
        kwh = wh / 1000
        cost = kwh * 0.12
        co2 = kwh * carbon_intensities[i]
        
        has_refactor = i in [0, 3, 5]
        
        run = {
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "code_snippet": code_snippets[i],
            "workload_type": workload_types[i],
            "total_joules": total_j,
            "total_wh": wh,
            "cost_usd": cost,
            "co2_grams": co2,
            "joule_score": scores[i],
            "region": regions[i],
            "carbon_intensity": carbon_intensities[i],
            "function_breakdown": mock_breakdowns[i],
            "ai_refactor_available": 1 if has_refactor else 0,
            "ai_summary": "Optimized loop structure and used vectorized operations." if has_refactor else None,
            "ai_refactored_code": None,
            "ai_energy_reduction_percent": random.randint(15, 45) if has_refactor else None,
        }
        
        insert_run(run)
