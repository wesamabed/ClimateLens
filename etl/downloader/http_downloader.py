# etl/downloader/http_downloader.py
import logging
import time
from pathlib import Path
from typing import Iterable, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests as _requests
from etl.downloader.protocols import Downloader

class HTTPDownloader(Downloader):
    """
    Downloads year‐tar.gz files via HTTPS with retry and parallelism.
    Implements the same interface as FTPDownloader.
    """
    def __init__(
        self,
        base_url: str = "https://www.ncei.noaa.gov/data/global-summary-of-the-day/archive",
        retry_attempts: int = 3,
        retry_wait: int = 5,
        logger: Optional[logging.Logger] = None,
        session: Optional[Any] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.retry_attempts = retry_attempts
        self.retry_wait = retry_wait
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.session = session or _requests

    def download_years(
        self,
        years: Iterable[int],
        dest_dir: Path,
        max_workers: int = 4,
    ) -> List[Path]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Parallel HTTP download for years: {list(years)}")
        start = time.perf_counter()
        results: List[Path] = []

        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="http-downloader") as exe:
            futures = {
                exe.submit(self.download_year_tar, y, dest_dir): y
                for y in years
            }
            try:
                for fut in as_completed(futures):
                    y = futures[fut]
                    try:
                       results.append(fut.result())
                    except Exception as e:
                        self.logger.error(f"✖ Year {y} failed: {e!r}")
            except KeyboardInterrupt:
                self.logger.warning("Interrupted, shutting down HTTP threads…")
                exe.shutdown(wait=False)
                raise
            finally:
                elapsed = time.perf_counter() - start
        self.logger.info(f"HTTP downloads complete in {elapsed:.1f}s")
        return results

    def download_year_tar(self, year: int, dest_dir: Path) -> Path:
        """
        Fetch {year}.tar.gz into dest_dir/{year}/{year}.tar.gz,
        retrying up to `retry_attempts` times.
        """
        year_dir = dest_dir / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{year}.tar.gz"
        out_path = year_dir / filename
        url = f"{self.base_url}/{year}.tar.gz"

        self.logger.info(f"Downloading HTTP {year} → {out_path}")
        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = self.session.get(url, stream=True, timeout=60)
                resp.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.logger.info(f"✔ Year {year} downloaded in attempt {attempt}")
                return out_path
            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt}/{self.retry_attempts} for year {year} failed: {e!r}"
                )
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_wait)
                else:
                    raise
