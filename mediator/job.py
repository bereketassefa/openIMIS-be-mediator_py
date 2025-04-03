# myapp/jobs.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def fetch_data_from_server():
    logger.info("Starting data fetch")
    print("Fetching data from server...")
    # try:
    #     response = requests.get('https://api.example.com/data', timeout=10)
    #     response.raise_for_status()
    #     data = response.json()
    #     logger.info("Data fetched successfully")
    #     # Process your data here (e.g., save to database)
    # except requests.RequestException as e:
    #     logger.error(f"Fetch failed: {e}")