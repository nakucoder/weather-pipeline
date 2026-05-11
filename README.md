# Miami Weather Pipeline

An automated data pipeline that fetches real-time weather data for Miami, FL and stores it in AWS S3 — built with FastAPI, AWS Lambda, and Python.

## What it does

- Fetches live weather data from Open-Meteo API (no API key needed)
- Transforms and cleans the data into structured JSON
- Automatically saves it to AWS S3 every 60 minutes
- Organized by date: `miami-weather/YYYY/MM/DD/HH-MM-SS.json`
- Exposes a REST API to trigger the pipeline manually or check current weather

## Data Storage

- Data is saved to S3 every 60 minutes automatically
- S3 path structure: `miami-weather/YYYY/MM/DD/HH-MM-SS.json`
- Each file contains temperature (°F and °C), feels like, high/low, humidity, wind speed, sunrise/sunset, condition, and hourly forecast
- The `/history` endpoint reads the last 7 days of S3 files and returns them as a JSON array sorted oldest to newest

## Tech Stack

- **FastAPI** — REST API framework
- **AWS Lambda** — serverless compute (replaces APScheduler + EC2)
- **Amazon EventBridge** — cron trigger, fires every 60 minutes
- **API Gateway** — REST endpoint: `GET /weather`
- **CloudWatch** — logs and error alarms
- **SNS** — email alerts on Lambda errors
- **AWS S3** — cloud storage for all pipeline data
- **Open-Meteo API** — free, no API key required

## Lambda Migration

The pipeline was migrated from EC2 + Docker + APScheduler to a fully serverless architecture on AWS Lambda.

- **Scheduling:** Amazon EventBridge triggers the Lambda function every hour, replacing APScheduler running on a long-lived EC2 instance
- **API access:** API Gateway exposes the `/weather` endpoint at `https://nj6nmdc5ge.execute-api.us-east-2.amazonaws.com/prod/weather`
- **Security:** The Lambda execution role uses IAM least-privilege permissions — no hardcoded credentials anywhere in the codebase
- **Observability:** CloudWatch captures all Lambda logs and monitors for errors; SNS sends email alerts on any Lambda failure

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Check if pipeline is running |
| `GET /health` | Health check for monitoring |
| `GET /weather` | Get current Miami weather (no S3 save) |
| `GET /run` | Trigger pipeline manually + save to S3 |
| `GET /history` | Get last 7 days of weather data from S3 |

**Live endpoint:** `https://nj6nmdc5ge.execute-api.us-east-2.amazonaws.com/prod/weather`

## How to run it

**Requirements:** Docker installed on your machine

1. Clone the repo: `git clone https://github.com/nakucoder/weather-pipeline.git`
2. Create a `.env` file with your AWS credentials
3. Run with Docker: `docker-compose up -d`
4. Test it: open `http://localhost:8000/run` in your browser

## Data Sample

```json
{
  "timestamp": "2026-04-30T15:38:03",
  "location": "Miami, FL",
  "temperature_celsius": 28.4,
  "temperature_fahrenheit": 83.1,
  "feels_like_celsius": 31.2,
  "feels_like_fahrenheit": 88.2,
  "high_fahrenheit": 90.1,
  "low_fahrenheit": 74.3,
  "wind_speed_kmh": 14.2,
  "condition": "Clear sky",
  "sunrise": "2026-04-30T06:38",
  "sunset": "2026-04-30T19:55",
  "hourly_forecast": [
    {
      "time": "2026-04-30T15:00",
      "temperature_celsius": 28.4,
      "temperature_fahrenheit": 83.1,
      "humidity": 58,
      "wind_speed": 14.2,
      "precipitation_probability": 5,
      "apparent_temperature_c": 31.2,
      "apparent_temperature_f": 88.2
    }
  ]
}
```

## Author

Juan Spinelli — [GitHub](https://github.com/nakucoder) | [LinkedIn](https://www.linkedin.com/in/juan-spinelli-85b6a1294)
