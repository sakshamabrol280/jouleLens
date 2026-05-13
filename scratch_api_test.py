import requests
import json

api_key = "em_live_nYz9WNkJbimnkpleZvEhVuV3LUlek8uGbZpRER"
zone = "US-CAL-CISO"
urls = [
    f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}",
    f"https://api-access.electricitymaps.com/free-tier/carbon-intensity/latest?zone={zone}",
    f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={zone}",
    f"https://api-access.electricitymaps.com/free-tier/carbon-intensity/forecast?zone={zone}",
    f"https://api.electricitymaps.com/v3/carbon-intensity/forecast?zone={zone}"
]

for url in urls:
    print(f"\n--- URL: {url} ---")
    try:
        res = requests.get(url, headers={"auth-token": api_key}, timeout=5)
        print("Status:", res.status_code)
        if res.status_code == 200:
            print("Success:", json.dumps(res.json(), indent=2)[:200])
        else:
            print("Response:", res.text)
    except Exception as e:
        print("Error:", e)
