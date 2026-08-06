import os
import requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

load_dotenv()
key_id = os.getenv("ALPACA_KEY_ID")
secret_key = os.getenv("ALPACA_SECRET_KEY")

headers = {"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret_key}
params = {"symbols":"AAPL", "start":"2025-08-05", "end":"2025-08-10", "limit":50, include}

response = requests.get("https://data.alpaca.markets/v1beta1/news", headers=headers, params=params, include_content=true)

print(response.status_code)
print(response.text)
