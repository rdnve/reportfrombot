import requests as requests_core
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=1, status_forcelist=[429], method_whitelist=["GET"], backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests_core.Session()

session.mount("https://", adapter=adapter)

__all__ = ["session"]
