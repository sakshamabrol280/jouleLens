"""
JouleLens — Carbon Intensity API Module.
Fetches live grid carbon intensity from ElectricityMaps API with mock fallback.
"""

import os
import math
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Mock carbon intensity data (gCO₂/kWh) for fallback
MOCK_CARBON_DATA = {
    "US-CAL-CISO": 210,
    "US-TEX-ERCO": 380,
    "US-NY-NYIS": 290,
    "GB": 185,
    "DE": 320,
    "FR": 58,
    "IN-SO": 620,
    "AU-NSW": 510,
    "JP-TK": 470,
    "BR-S": 95,
    "ZA": 680,
    "SG": 430,
}

# Zone display names
ZONE_NAMES = {
    "US-CAL-CISO": "🇺🇸 California (CAISO)",
    "US-TEX-ERCO": "🇺🇸 Texas (ERCOT)",
    "US-NY-NYIS": "🇺🇸 New York (NYISO)",
    "GB": "🇬🇧 Great Britain",
    "DE": "🇩🇪 Germany",
    "FR": "🇫🇷 France",
    "IN-SO": "🇮🇳 India (Southern)",
    "AU-NSW": "🇦🇺 Australia (NSW)",
    "JP-TK": "🇯🇵 Japan (Tokyo)",
    "BR-S": "🇧🇷 Brazil (South)",
    "ZA": "🇿🇦 South Africa",
    "SG": "🇸🇬 Singapore",
}


def get_carbon_intensity(zone_code):
    """
    Fetch current carbon intensity for a zone.
    Uses ElectricityMaps API if key available, otherwise mock data.
    
    Returns: {"carbon_intensity": float, "zone": str, "is_mock": bool}
    """
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY", "").strip()
    
    if api_key:
        try:
            response = requests.get(
                f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone_code}",
                headers={"auth-token": api_key},
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "carbon_intensity": data.get("carbonIntensity", 300),
                    "zone": zone_code,
                    "is_mock": False,
                }
        except (requests.RequestException, KeyError, ValueError):
            pass  # Fall through to mock data
    
    # Fallback to mock data
    intensity = MOCK_CARBON_DATA.get(zone_code, 300)
    return {
        "carbon_intensity": intensity,
        "zone": zone_code,
        "is_mock": True,
    }


def get_carbon_forecast_mock(zone_code):
    """
    Generate a 24-hour mock carbon intensity forecast using sinusoidal patterns.
    Simulates day/night renewable energy variation.
    
    Returns: list of {"hour": int, "carbon_intensity": float, "timestamp": str}
    """
    base = MOCK_CARBON_DATA.get(zone_code, 300)
    amplitude = base * 0.3
    now = datetime.now()
    current_hour = now.hour
    
    forecast = []
    for h in range(24):
        future_hour = (current_hour + h) % 24
        # Sinusoidal pattern: lower at midday (solar peak), higher at night
        # Minimum around hour 13 (1 PM), maximum around hour 1 (1 AM)
        intensity = base + amplitude * math.sin(math.radians((future_hour - 1) * 15))
        # Add some noise
        import random
        noise = random.uniform(-base * 0.05, base * 0.05)
        intensity = max(10, intensity + noise)
        
        timestamp = (now + timedelta(hours=h)).strftime("%Y-%m-%d %H:%M")
        forecast.append({
            "hour": h,
            "actual_hour": future_hour,
            "carbon_intensity": round(intensity, 1),
            "timestamp": timestamp,
        })
    
    return forecast


def get_best_window(forecast_data, window_size=3):
    """
    Find the best N-hour window with lowest average carbon intensity.
    
    Returns: {"best_start_hour": int, "best_avg_intensity": float, 
              "current_intensity": float, "savings_percent": float}
    """
    if not forecast_data or len(forecast_data) < window_size:
        return {
            "best_start_hour": 0,
            "best_avg_intensity": 300,
            "current_intensity": 300,
            "savings_percent": 0,
        }
    
    current_intensity = forecast_data[0]["carbon_intensity"]
    
    best_avg = float("inf")
    best_start = 0
    
    for i in range(len(forecast_data) - window_size + 1):
        window = forecast_data[i:i + window_size]
        avg = sum(d["carbon_intensity"] for d in window) / window_size
        if avg < best_avg:
            best_avg = avg
            best_start = i
    
    savings_percent = 0
    if current_intensity > 0:
        savings_percent = max(0, (current_intensity - best_avg) / current_intensity * 100)
    
    return {
        "best_start_hour": best_start,
        "best_avg_intensity": round(best_avg, 1),
        "current_intensity": round(current_intensity, 1),
        "savings_percent": round(savings_percent, 1),
    }


def get_grid_status(carbon_intensity):
    """
    Classify grid status based on carbon intensity.
    
    Returns: (label: str, color: str)
    """
    if carbon_intensity < 100:
        return ("🟢 Clean Grid", "green")
    elif carbon_intensity < 250:
        return ("🟡 Mixed Grid", "orange")
    else:
        return ("🔴 Carbon Heavy", "red")
