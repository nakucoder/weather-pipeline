from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.weather import fetch_miami_weather
from app.storage import save_to_s3
from app.config import PIPELINE_INTERVAL_MINUTES

app = FastAPI(
    title="Miami Weather Pipeline",
    description="Automated weather data pipeline for Miami, FL",
    version="1.0.0"
)

# --- Pipeline Function ---
def run_pipeline():
    """Fetches weather data and saves it to S3."""
    print("Running weather pipeline...")
    weather_data = fetch_miami_weather()
    if weather_data:
        save_to_s3(weather_data)
        print(f"Pipeline complete: {weather_data['timestamp']}")
    else:
        print("Pipeline failed: no data returned")

# --- Scheduler (runs every 60 minutes automatically) ---
scheduler = BackgroundScheduler()
scheduler.add_job(run_pipeline, "interval", minutes=PIPELINE_INTERVAL_MINUTES)
scheduler.start()

# --- API Endpoints ---
@app.get("/")
def root():
    return {"message": "Miami Weather Pipeline is running"}

@app.get("/health")
def health():
    return {"status": "healthy", "scheduler": "running"}

@app.get("/run")
def trigger_pipeline():
    """Manually trigger the pipeline without waiting for the schedule."""
    weather_data = fetch_miami_weather()
    if weather_data:
        filename = save_to_s3(weather_data)
        return {"status": "success", "data": weather_data, "saved_to": filename}
    return {"status": "error", "message": "Failed to fetch weather data"}

@app.get("/weather")
def get_current_weather():
    """Get current Miami weather without saving to S3."""
    weather_data = fetch_miami_weather()
    if weather_data:
        return {"status": "success", "data": weather_data}
    return {"status": "error", "message": "Failed to fetch weather data"}