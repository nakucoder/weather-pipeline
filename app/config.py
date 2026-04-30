import os
from dotenv import load_dotenv

load_dotenv()

# AWS Settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Weather Settings
MIAMI_LATITUDE = 25.7617
MIAMI_LONGITUDE = -80.1918
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Pipeline Settings
PIPELINE_INTERVAL_MINUTES = 60