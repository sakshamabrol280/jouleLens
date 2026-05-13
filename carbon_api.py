"""
JouleLens — Carbon Intensity API Module.
Fetches live grid carbon intensity from ElectricityMaps API with mock fallback.
"""

import os
import math
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

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
    Uses UK Carbon Intensity API for Great Britain (free, no key).
    Uses ElectricityMaps API for others if key available, otherwise mock data.
    
    Returns: {"carbon_intensity": float, "zone": str, "is_mock": bool}
    """
    if zone_code == "GB":
        try:
            res = requests.get("https://api.carbonintensity.org.uk/intensity", timeout=5)
            if res.status_code == 200:
                data = res.json()
                intensity = data["data"][0]["intensity"]["actual"]
                if intensity is None:
                    intensity = data["data"][0]["intensity"]["forecast"]
                return {
                    "carbon_intensity": intensity,
                    "zone": zone_code,
                    "is_mock": False,
                }
        except Exception:
            pass # Fall back to mock
            
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY", "").strip()
    
    if api_key:
        urls = [
            f"https://api-access.electricitymaps.com/free-tier/carbon-intensity/latest?zone={zone_code}",
            f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone_code}",
            f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={zone_code}"
        ]
        for url in urls:
            try:
                response = requests.get(url, headers={"auth-token": api_key}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "error" not in data and "carbonIntensity" in data:
                        return {
                            "carbon_intensity": data["carbonIntensity"],
                            "zone": zone_code,
                            "is_mock": False,
                        }
            except (requests.RequestException, KeyError, ValueError):
                continue
    
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


def get_carbon_forecast(zone_code):
    """
    Fetch 24-hour carbon intensity forecast for a zone from API.
    Uses UK Carbon Intensity API for Great Britain (free, no key).
    Falls back to mock data if API key is invalid or request fails.
    """
    if zone_code == "GB":
        try:
            res = requests.get("https://api.carbonintensity.org.uk/intensity/fw24h", timeout=5)
            if res.status_code == 200:
                data = res.json()
                forecast = []
                now = datetime.now()
                # The API returns 48 half-hour blocks. We take every other item for hourly data.
                for i in range(0, min(48, len(data["data"])), 2):
                    block = data["data"][i]
                    intensity = block["intensity"]["forecast"]
                    hour_idx = i // 2
                    timestamp = (now + timedelta(hours=hour_idx)).strftime("%Y-%m-%d %H:%M")
                    
                    forecast.append({
                        "hour": hour_idx,
                        "actual_hour": (now.hour + hour_idx) % 24,
                        "carbon_intensity": round(intensity, 1),
                        "timestamp": timestamp,
                    })
                if forecast:
                    return forecast
        except Exception:
            pass # Fall back to mock
            
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY", "").strip()
    
    if api_key:
        urls = [
            f"https://api-access.electricitymaps.com/free-tier/carbon-intensity/forecast?zone={zone_code}",
            f"https://api.electricitymap.org/v3/carbon-intensity/forecast?zone={zone_code}",
            f"https://api.electricitymaps.com/v3/carbon-intensity/forecast?zone={zone_code}"
        ]
        for url in urls:
            try:
                response = requests.get(url, headers={"auth-token": api_key}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "error" not in data and "forecast" in data:
                        forecast = []
                        now = datetime.now()
                        current_hour = now.hour
                        # Limit to next 24 hours
                        for i, f in enumerate(data["forecast"][:24]):
                            intensity = f.get("carbonIntensity", 300)
                            timestamp = (now + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M")
                            forecast.append({
                                "hour": i,
                                "actual_hour": (current_hour + i) % 24,
                                "carbon_intensity": round(intensity, 1),
                                "timestamp": timestamp,
                            })
                        if forecast:
                            return forecast
            except (requests.RequestException, KeyError, ValueError):
                continue
                
    return get_carbon_forecast_mock(zone_code)


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
