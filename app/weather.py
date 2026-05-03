import requests
from datetime import datetime
from app.config import MIAMI_LATITUDE, MIAMI_LONGITUDE, WEATHER_API_URL

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm"
}

def fetch_miami_weather():
    params = {
        "latitude": MIAMI_LATITUDE,
        "longitude": MIAMI_LONGITUDE,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability,apparent_temperature",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "timezone": "America/New_York",
        "forecast_days": 3
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        current = data["current_weather"]
        hourly = data["hourly"]
        daily = data["daily"]

        current_hour_index = datetime.now().hour

        hourly_forecast = []
        for i in range(current_hour_index, min(current_hour_index + 7, len(hourly["time"]))):
            temp_c = hourly["temperature_2m"][i]
            hourly_forecast.append({
                "time": hourly["time"][i],
                "temperature_celsius": temp_c,
                "temperature_fahrenheit": round((temp_c * 9/5) + 32, 1),
                "humidity": hourly["relative_humidity_2m"][i],
                "wind_speed": hourly["wind_speed_10m"][i],
                "precipitation_probability": hourly["precipitation_probability"][i],
                "apparent_temperature_c": hourly["apparent_temperature"][i],
                "apparent_temperature_f": round((hourly["apparent_temperature"][i] * 9/5) + 32, 1)
            })

        feels_like_c = hourly["apparent_temperature"][current_hour_index]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "location": "Miami, FL",
            "temperature_celsius": current["temperature"],
            "temperature_fahrenheit": round((current["temperature"] * 9/5) + 32, 1),
            "feels_like_celsius": feels_like_c,
            "feels_like_fahrenheit": round((feels_like_c * 9/5) + 32, 1),
            "wind_speed_kmh": current["windspeed"],
            "wind_direction": current["winddirection"],
            "weather_code": current["weathercode"],
            "condition": WEATHER_CODES.get(current["weathercode"], "Unknown"),
            "is_day": bool(current["is_day"]),
            "high_fahrenheit": round((daily["temperature_2m_max"][0] * 9/5) + 32, 1),
            "low_fahrenheit": round((daily["temperature_2m_min"][0] * 9/5) + 32, 1),
            "high_celsius": daily["temperature_2m_max"][0],
            "low_celsius": daily["temperature_2m_min"][0],
            "sunrise": daily["sunrise"][0],
            "sunset": daily["sunset"][0],
            "hourly_forecast": hourly_forecast
        }
    except Exception as e:
        print(f"Weather error: {e}")
        return None
