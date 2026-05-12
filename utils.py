"""
JouleLens — Utility Helpers.
Shared formatting functions, score mappings, and region data.
"""

from collections import OrderedDict


def format_joules(j):
    """Smart formatter for Joule values."""
    if j < 0.001:
        return f"{j * 1000:.2f} mJ"
    elif j < 1:
        return f"{j:.3f} J"
    else:
        return f"{j:.2f} J"


def format_currency(usd):
    """Format cost with appropriate precision."""
    if usd < 0.001:
        return f"₹{usd:.6f}"
    elif usd < 1:
        return f"₹{usd:.5f}"
    else:
        return f"₹{usd:.4f}"


def format_co2(grams):
    """Format CO2 emissions with appropriate unit."""
    if grams < 0.001:
        return f"{grams * 1000:.3f} mg CO2"
    elif grams < 1:
        return f"{grams * 1000:.1f} mg CO2"
    elif grams < 1000:
        return f"{grams:.3f} g CO2"
    else:
        return f"{grams / 1000:.3f} kg CO2"


def score_to_color(score):
    colors = {"A": "#00FF88", "B": "#3FB950", "C": "#F0A500", "D": "#FF8C00", "F": "#FF4B4B"}
    return colors.get(score, "#8B949E")


def score_to_label(score):
    labels = {"A": "Excellent", "B": "Good", "C": "Fair", "D": "Poor", "F": "Critical"}
    return labels.get(score, "Unknown")


def score_to_css_class(score):
    return f"score-{score.lower()}" if score in "ABCDF" else "score-c"


def truncate_code(code, max_chars=100):
    if not code:
        return ""
    code = code.strip().replace("\n", " | ")
    if len(code) > max_chars:
        return code[:max_chars] + "..."
    return code


def get_region_options():
    return OrderedDict([
        ("California (CAISO)", "US-CAL-CISO"),
        ("Texas (ERCOT)", "US-TEX-ERCO"),
        ("New York (NYISO)", "US-NY-NYIS"),
        ("Great Britain", "GB"),
        ("Germany", "DE"),
        ("France", "FR"),
        ("India (Southern)", "IN-SO"),
        ("Australia (NSW)", "AU-NSW"),
        ("Japan (Tokyo)", "JP-TK"),
        ("Brazil (South)", "BR-S"),
        ("South Africa", "ZA"),
        ("Singapore", "SG"),
    ])


def get_zone_display_name(zone_code):
    regions = get_region_options()
    for display, code in regions.items():
        if code == zone_code:
            return display
    return zone_code


DEMO_SNIPPETS = {
    "Demo 1 - Inefficient Loop": '''# Naive prime finder - energy inefficient
def find_primes(n):
    primes = []
    for num in range(2, n):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
        if is_prime:
            primes.append(num)
    return primes

result = find_primes(5000)
print(f"Found {len(result)} primes")
''',
    "Demo 2 - Matrix Multiply": '''import random
def matrix_multiply_naive(size):
    A = [[random.random() for _ in range(size)] for _ in range(size)]
    B = [[random.random() for _ in range(size)] for _ in range(size)]
    C = [[0]*size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                C[i][j] += A[i][k] * B[k][j]
    return C

result = matrix_multiply_naive(100)
''',
    "Demo 3 - Efficient Fibonacci": '''from functools import lru_cache
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

results = [fibonacci(i) for i in range(50)]
print(results[-1])
''',
}
