# Normalizes all time formats into a uniform timezone and format

from datetime import datetime, timezone

def alpaca_timezone_normalizer(alpaca_time_raw):
    return datetime.fromisoformat(alpaca_time_raw)
    

def finnhub_timezone_normalizer(finnhub_time_raw):
    return datetime.fromtimestamp(finnhub_time_raw, tz=timezone.utc)


def alpha_vantage_timezone_normalizer(alpha_vantage_time_raw):
    dt = datetime.strptime(alpha_vantage_time_raw, "%Y%m%dT%H%M%S")
    return dt.replace(tzinfo=timezone.utc)

