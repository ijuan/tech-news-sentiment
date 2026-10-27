"""One shared way to call any news API: timeout + automatic retries."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT_SECONDS = 15


def build_session() -> requests.Session:
    retry = Retry(
        total=3,                                   # up to 3 retries after the first try
        backoff_factor=2,                          # wait 2s, 4s, 8s between attempts
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,           # if the API says "wait 30s", wait 30s
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def get_json(session: requests.Session, url: str, *, params=None, headers=None):
    response = session.get(url, params=params, headers=headers, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()                    # 4xx/5xx that survived retries -> exception
    return response.json()
