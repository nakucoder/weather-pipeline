Miami Weather Pipeline
An automated data pipeline that fetches real-time weather data for Miami, FL and stores it in AWS S3 — built with FastAPI, Docker, and Python.
What it does

Fetches live weather data from Open-Meteo API (no API key needed)
Transforms and cleans the data into structured JSON
Automatically saves it to AWS S3 every 60 minutes
Organized by date: miami-weather/YYYY/MM/DD/HH-MM-SS.json
Exposes a REST API to trigger the pipeline manually or check current weather

Tech Stack

FastAPI — REST API framework
Docker — containerized for consistent deployment anywhere
AWS S3 — cloud storage for all pipeline data
APScheduler — automated scheduling (runs every 60 minutes)
Open-Meteo API — free, no API key required

API Endpoints
EndpointDescriptionGET /Check if pipeline is runningGET /healthHealth check for monitoringGET /weatherGet current Miami weather (no S3 save)GET /runTrigger pipeline manually + save to S3
How to run it
Requirements: Docker installed on your machine
1. Clone the repo:
git clone https://github.com/nakucoder/weather-pipeline.git
2. Set up environment variables — create a .env file with your AWS credentials
3. Run with Docker:
docker-compose up --build
4. Test it: open http://localhost:8000/run in your browser
Data Sample
Each pipeline run saves a JSON file like this to S3:
{"timestamp": "2026-04-30T15:38:03", "location": "Miami, FL", "temperature_celsius": 28.4, "temperature_fahrenheit": 83.1, "wind_speed_kmh": 14.2}
Author
Juan Spinelli — GitHub | LinkedIn
