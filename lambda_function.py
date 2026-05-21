import boto3
import json
import os
import requests
from datetime import datetime

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm"
}

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
MIAMI_LATITUDE = 25.7617
MIAMI_LONGITUDE = -80.1918

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
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
    response = requests.get(WEATHER_API_URL, params=params, timeout=15)
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
            "temperature_fahrenheit": round((temp_c * 9 / 5) + 32, 1),
            "humidity": hourly["relative_humidity_2m"][i],
            "wind_speed": hourly["wind_speed_10m"][i],
            "precipitation_probability": hourly["precipitation_probability"][i],
            "apparent_temperature_c": hourly["apparent_temperature"][i],
            "apparent_temperature_f": round((hourly["apparent_temperature"][i] * 9 / 5) + 32, 1)
        })

    feels_like_c = hourly["apparent_temperature"][current_hour_index]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Miami, FL",
        "temperature_celsius": current["temperature"],
        "temperature_fahrenheit": round((current["temperature"] * 9 / 5) + 32, 1),
        "feels_like_celsius": feels_like_c,
        "feels_like_fahrenheit": round((feels_like_c * 9 / 5) + 32, 1),
        "wind_speed_kmh": current["windspeed"],
        "wind_direction": current["winddirection"],
        "weather_code": current["weathercode"],
        "condition": WEATHER_CODES.get(current["weathercode"], "Unknown"),
        "is_day": bool(current["is_day"]),
        "high_fahrenheit": round((daily["temperature_2m_max"][0] * 9 / 5) + 32, 1),
        "low_fahrenheit": round((daily["temperature_2m_min"][0] * 9 / 5) + 32, 1),
        "high_celsius": daily["temperature_2m_max"][0],
        "low_celsius": daily["temperature_2m_min"][0],
        "sunrise": daily["sunrise"][0],
        "sunset": daily["sunset"][0],
        "hourly_forecast": hourly_forecast
    }


def transform_record(raw):
    ts = datetime.fromisoformat(raw["timestamp"])
    time_str = ts.strftime("%m/%d %H:%M")

    humidity = None
    hourly = raw.get("hourly_forecast", [])
    if hourly:
        humidity = hourly[0].get("humidity")

    wind_mph = round(raw["wind_speed_kmh"] / 1.60934)

    sunrise = raw.get("sunrise", "")
    if "T" in sunrise:
        sunrise = sunrise.split("T")[1][:5]

    sunset = raw.get("sunset", "")
    if "T" in sunset:
        sunset = sunset.split("T")[1][:5]

    return {
        "time": time_str,
        "temp": raw["temperature_fahrenheit"],
        "feels_like": raw["feels_like_fahrenheit"],
        "high": raw["high_fahrenheit"],
        "low": raw["low_fahrenheit"],
        "humidity": humidity,
        "wind_mph": wind_mph,
        "sunrise": sunrise,
        "sunset": sunset,
        "condition": raw["condition"],
    }


HISTORY_KEY = "miami-weather/history.json"


def fetch_weather_history(bucket):
    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=bucket, Key=HISTORY_KEY)
        return json.loads(obj["Body"].read())
    except s3.exceptions.NoSuchKey:
        return []


def update_weather_history(s3, bucket, new_entry):
    try:
        obj = s3.get_object(Bucket=bucket, Key=HISTORY_KEY)
        history = json.loads(obj["Body"].read())
    except s3.exceptions.NoSuchKey:
        history = []

    history.append(new_entry)
    history = history[-168:]

    s3.put_object(
        Bucket=bucket,
        Key=HISTORY_KEY,
        Body=json.dumps(history),
        ContentType="application/json",
    )


def handler(event, context):
    path = event.get("path") or event.get("rawPath") or ""
    bucket = os.environ["AWS_BUCKET_NAME"]

    if path == "/weather/history":
        try:
            data = fetch_weather_history(bucket)
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"status": "success", "data": data}),
            }
        except Exception as e:
            print(f"History error: {e}")
            return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"error": str(e)})}

    try:
        weather_data = fetch_miami_weather()

        timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H-%M-%S")
        key = f"miami-weather/{timestamp}.json"

        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(weather_data, indent=2),
            ContentType="application/json"
        )

        update_weather_history(s3, bucket, transform_record(weather_data))
        print(f"Saved to s3://{bucket}/{key}")
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(weather_data),
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"error": str(e)})}
