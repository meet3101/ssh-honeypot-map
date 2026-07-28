import requests

def geolocate(ip):
    try:
        if ip.startswith(("10.", "172.", "192.168.", "127.")):
            return {"country": "Local/Private", "city": "N/A", "lat": 0, "lon": 0}

        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = resp.json()
        if data.get("status") == "success":
            return {
                "country": data.get("country"),
                "city": data.get("city"),
                "lat": data.get("lat"),
                "lon": data.get("lon")
            }
    except Exception:
        pass
    return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0}
