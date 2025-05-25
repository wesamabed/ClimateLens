# etl/downloader/co2_downloader.py

import logging
import time
from pathlib import Path
from typing import Iterable, List, Any, Optional, Mapping

import requests
from etl.downloader.protocols import Downloader


class CO2Downloader(Downloader):
    """
    Downloads CO₂ emissions data for a given indicator from the
    World Bank API, over a span of years, with retry support.
    """

    def __init__(
        self,
        indicator: str,
        retry_attempts: int = 3,
        retry_wait: int = 5,
        session: Optional[requests.Session] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.indicator      = indicator
        self.retry_attempts = retry_attempts
        self.retry_wait     = retry_wait
        self.session        = session or requests.Session()
        self.logger         = logger or logging.getLogger(self.__class__.__name__)

    def download_years(
        self,
        years: Iterable[int],
        dest_dir: Optional[Path] = None,
        max_workers: int = 1,
    ) -> List[Mapping[str, Any]]:
        """
        Fetch CO₂ JSON for `self.indicator` across the [min(years), max(years)] range.
        `dest_dir` and `max_workers` are accepted for interface compatibility but unused.
        Returns the list of raw records (the second element of the JSON response).
        """
        start, end = min(years), max(years)
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/"
            f"{self.indicator}?date={start}:{end}&format=json&per_page=20000"
        )
        self.logger.info(f"Downloading CO₂ indicator {self.indicator} for {start}–{end}")
        self.logger.debug(f"GET {url}")

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = self.session.get(url, timeout=60)
                resp.raise_for_status()
                payload = resp.json()
                # payload[0] is metadata, payload[1] is the data list
                if not (isinstance(payload, list) and len(payload) >= 2):
                    raise ValueError("Unexpected API response shape")
                records = payload[1]
                self.logger.info(f"✔ Retrieved {len(records)} records on attempt {attempt}")
                return records
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Attempt {attempt}/{self.retry_attempts} failed: {e!r}"
                )
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_wait)
                else:
                    self.logger.error(
                        f"All {self.retry_attempts} CO₂ download attempts failed"
                    )

        # if we exit the loop without returning, re-raise the last error
        raise last_error  # type: ignore
