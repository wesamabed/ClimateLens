from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Iterable, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from tenacity import retry, stop_after_attempt, wait_fixed, before_log

from etl.downloader.protocols import Downloader, FTPClientInterface
from etl.downloader.ftp_client import DefaultFTPClient

class FTPDownloader(Downloader):
    """
    Downloads year‐tar files via FTP with retry and parallelism.
    Applies dependency injection by allowing a custom FTP client adapter.
    """
    def __init__(
        self,
        host: str = "ftp.ncei.noaa.gov",
        user: str = "anonymous",
        passwd: str = "",
        retry_attempts: int = 3,
        retry_wait: int = 5,
        logger: Optional[logging.Logger] = None,
        ftp_client: Optional[FTPClientInterface] = None,
    ) -> None:
        self.host = host
        self.user = user
        self.passwd = passwd
        self.retry_attempts = retry_attempts
        self.retry_wait = retry_wait
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.ftp_client = ftp_client or DefaultFTPClient()

    def download_years(self, years: Iterable[int], dest_dir: Path, max_workers: int = 4) -> List[Path]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("Parallel download for years: %s", list(years))
        t0 = time.perf_counter()
        results: List[Path] = []

        with ThreadPoolExecutor(max_workers=max_workers) as exe:
            futures = {exe.submit(self.download_year_tar, year, dest_dir): year for year in years}
            for fut in as_completed(futures):
                year = futures[fut]
                try:
                    results.append(fut.result())
                except Exception as e:
                    self.logger.error("✖ Year %d failed: %r", year, e)

        self.logger.info("All downloads complete in %.1f s", time.perf_counter() - t0)
        return results

    def download_year_tar(self, year: int, dest_dir: Path) -> Path:
        """
        Fetch gsod_{year}.tar into dest_dir/{year}/gsod_{year}.tar,
        retrying up to `retry_attempts` times.
        """
        year_dir = dest_dir / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        out = year_dir / f"gsod_{year}.tar"

        self.logger.info("Downloading GSOD %d → %s", year, out)

        @retry(
            stop=stop_after_attempt(self.retry_attempts),
            wait=wait_fixed(self.retry_wait),
            before=before_log(self.logger, logging.INFO),
            reraise=True,
        )
        def _do_download() -> Path:
            t0 = time.perf_counter()
            with self.ftp_client.login_and_cwd(self.host, self.user, self.passwd, year) as ftp:
                with open(out, "wb") as f:
                    ftp.retrbinary(f"RETR gsod_{year}.tar", f.write)
            self.logger.info("Year %d done in %.1f s", year, time.perf_counter() - t0)
            return out

        return _do_download()