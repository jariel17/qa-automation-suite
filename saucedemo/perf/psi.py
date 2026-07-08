import os
import time
from functools import lru_cache
from typing import Any, cast

import requests

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PSI_TIMEOUT_SECONDS = 60
PSI_MAX_ATTEMPTS = 3
PSI_RETRY_BACKOFFS_SECONDS = (3, 5)


@lru_cache(maxsize=None)
def fetch_psi_result(url: str, strategy: str) -> dict[str, Any]:
    """Run a PageSpeed Insights Lighthouse audit for url/strategy and return the raw JSON.

    Retries up to PSI_MAX_ATTEMPTS times on a transient server error (5xx) or a read timeout, 
    with a growing backoff between attempts
    (PSI_RETRY_BACKOFFS_SECONDS). A 4xx (bad key, quota exceeded) fails immediately since a
    retry would not fix it.
    """
    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
        "key": os.environ["PSI_API_KEY"],
    }

    for attempt in range(1, PSI_MAX_ATTEMPTS + 1):
        try:
            response = requests.get(PSI_ENDPOINT, params=params, timeout=PSI_TIMEOUT_SECONDS)
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except requests.exceptions.Timeout:
            if attempt == PSI_MAX_ATTEMPTS:
                raise
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code is None or status_code < 500 or attempt == PSI_MAX_ATTEMPTS:
                raise
        if attempt < PSI_MAX_ATTEMPTS:
            time.sleep(PSI_RETRY_BACKOFFS_SECONDS[attempt - 1])

    raise RuntimeError("PSI retry loop exited without returning or raising")
