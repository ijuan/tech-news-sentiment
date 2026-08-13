import os
import requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")
key_id = os.getenv("FINNHUB_KEY")


headers = {"X-Finnhub-Token" : key_id}
params = {"symbol": "AAPL", "from": "2026-08-05", "to": "2026-08-06"}

response = requests.get("https://finnhub.io/api/v1/company-news", headers=headers, params=params,)

print(response.status_code)
print(response.text)
