import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")
api_key = os.getenv("ALPHAVANTAGE_KEY")

params = {"apikey": api_key, "tickers": "AAPL", "function": "NEWS_SENTIMENT", "time_from": "20250805T0000", "time_to": "20250810T0000", "limit": 50}

response = requests.get("https://www.alphavantage.co/query", params=params)

print(response.status_code)
print(response.text)