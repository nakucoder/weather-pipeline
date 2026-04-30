import requests
from datetime import datetime
from app.config import MIAMI_LATITUDE, MIAMI_LONGITUDE, WEATHER_API_URL

def fetch_miami_weather():
    """
    Fetches current weather data for Miami from Open-Meteo API.
    No API key needed - completely free.
    """
    params = {
        "latitude": MIAMI_LATITUDE,
        "longitude": MIAMI_LONGITUDE,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
    }

    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract what we care about
        current = data["current_weather"]

        weather = {
            "timestamp": datetime.utcnow().isoformat(),
            "location": "Miami, FL",
            "temperature_celsius": current["temperature"],
            "temperature_fahrenheit": round((current["temperature"] * 9/5) + 32, 1),
            "wind_speed_kmh": current["windspeed"],
            "wind_direction": current["winddirection"],
            "weather_code": current["weathercode"],
            "is_day": bool(current["is_day"]),
        }

        return weather

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None