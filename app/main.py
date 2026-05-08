import boto3
import json
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.weather import fetch_miami_weather
from app.storage import save_to_s3
from app.config import PIPELINE_INTERVAL_MINUTES, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME, AWS_REGION

app = FastAPI(title="Miami Weather Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_pipeline():
    print("Running weather pipeline...")
    weather_data = fetch_miami_weather()
    if weather_data:
        save_to_s3(weather_data)
        print(f"Pipeline complete: {weather_data['timestamp']}")
    else:
        print("Pipeline failed: no data returned")

scheduler = BackgroundScheduler()
scheduler.add_job(run_pipeline, "interval", minutes=PIPELINE_INTERVAL_MINUTES)
scheduler.start()

@app.get("/")
def root():
    return {"message": "Miami Weather Pipeline is running"}

@app.get("/health")
def health():
    return {"status": "healthy", "scheduler": "running"}

@app.get("/run")
def trigger_pipeline():
    weather_data = fetch_miami_weather()
    if weather_data:
        filename = save_to_s3(weather_data)
        return {"status": "success", "data": weather_data, "saved_to": filename}
    return {"status": "error", "message": "Failed to fetch weather data"}

@app.get("/weather")
def get_current_weather():
    weather_data = fetch_miami_weather()
    if weather_data:
        return {"status": "success", "data": weather_data}
    return {"status": "error", "message": "Failed to fetch weather data"}

@app.get("/history")
def get_history():
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=AWS_BUCKET_NAME, Prefix="miami-weather/")

        entries = []
        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                # key format: miami-weather/YYYY/MM/DD/HH-MM-SS.json
                parts = key.removeprefix("miami-weather/").removesuffix(".json").split("/")
                if len(parts) != 4:
                    continue
                year, month, day, time_part = parts
                hour, minute, second = time_part.split("-")
                file_dt = datetime(
                    int(year), int(month), int(day),
                    int(hour), int(minute), int(second),
                    tzinfo=timezone.utc,
                )
                if file_dt >= cutoff:
                    entries.append((file_dt, key))

        entries.sort(key=lambda x: x[0])

        results = []
        for file_dt, key in entries:
            body = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=key)["Body"].read()
            data = json.loads(body)
            results.append({
                "time": file_dt.strftime("%m/%d %H:%M"),
                "temp": data["temperature_fahrenheit"],
                "feels_like": data["feels_like_fahrenheit"],
                "high": data["high_fahrenheit"],
                "low": data["low_fahrenheit"],
                "humidity": data["hourly_forecast"][0]["humidity"],
                "wind_mph": round(data["wind_speed_kmh"] * 0.621371),
                "sunrise": data["sunrise"].split("T")[1][:5],
                "sunset": data["sunset"].split("T")[1][:5],
                "condition": data["condition"],
            })

        return {"status": "success", "data": results}

    except Exception as e:
        return {"status": "error", "message": str(e)}
