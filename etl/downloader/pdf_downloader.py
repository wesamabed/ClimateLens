import logging
import pathlib
import time
import requests
from typing import Optional
from etl.downloader.protocols import Downloader

class PDFDownloader(Downloader):
    """
    Download a single PDF once; if the file already exists we just return the path.
    """
    def __init__(
        self,
        url: str,
        dest_dir: pathlib.Path,
        retry_attempts: int,
        retry_wait: int,
        logger: Optional[logging.Logger] = None,
    ):
        self.url, self.dest_dir = url, dest_dir
        self.retry_attempts, self.retry_wait = retry_attempts, retry_wait
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    # keep the same method name used by other downloaders so a generic Step can call it
    def download_years(self, years=None, dest_dir=None, max_workers=1):   # type: ignore
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        filename = pathlib.Path(self.url).name
        out_path = self.dest_dir / filename
        if out_path.exists():
            self.logger.info(f"PDF already present → {out_path}")
            return [out_path]

        self.logger.info(f"Downloading IPCC PDF → {out_path}")
        for attempt in range(1, self.retry_attempts + 1):
            try:
                start = time.perf_counter()
                resp = requests.get(self.url, timeout=60, stream=True)
                resp.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                self.logger.info(
                    f"✔ PDF downloaded ({out_path.stat().st_size/1e6:.1f} MB) "
                    f"in {time.perf_counter()-start:.1f}s"
                )
                return [out_path]
            except Exception as e:
                self.logger.warning(f"Attempt {attempt} failed: {e!r}")
                if attempt == self.retry_attempts:
                    raise
                time.sleep(self.retry_wait)
