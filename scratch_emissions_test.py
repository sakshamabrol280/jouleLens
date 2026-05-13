import requests
import json

api_key = "em_live_nYz9WNkJbimnkpleZvEhVuV3LUlek8uGbZpRER"
zone = "US" # emissions.dev might use country codes instead of zone codes

url = "https://api.emissions.dev/v1/electricity/grid"
print(f"--- URL: {url} ---")
try:
    res = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=5)
    print("Status:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("Success:")
        # Just print first 2 items to see structure
        print(json.dumps(data[:2] if isinstance(data, list) else data, indent=2)[:500])
    else:
        print("Response:", res.text)
except Exception as e:
    print("Error:", e)
