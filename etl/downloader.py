# etl/downloader.py
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type
)
from etl.logger import get_logger

logger = get_logger(__name__, level="INFO")

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def _fetch(url: str, timeout: int = 60):
    """Decorator handles retries on network/HTTP errors."""
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    return resp

def download_year(year: int, target_dir: Path) -> Optional[Path]:
    """
    Download GSOD CSV for a given year:
      • Builds URL dynamically
      • Skips existing files (Performance)
      • Streams with tqdm (Accessibility)
      • Retries + exponential backoff (Reliability)
      • Logs all steps via adapter (Maintainability)
      • Fails gracefully returning None (Scalability)
    """
    url = f"https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/gsod_{year}.csv"
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    out_file = target_dir / f"gsod_{year}.csv"
    if out_file.exists():
        logger.debug("Skipping year %d; already downloaded at %s", year, out_file)
        return out_file

    try:
        logger.info("Downloading year %d from %s", year, url)
        resp = _fetch(url)
        total = int(resp.headers.get("content-length", 0))
        with open(out_file, "wb") as f, tqdm(
            total=total, unit="iB", unit_scale=True, desc=f"Year {year}", leave=False
        ) as bar:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        logger.info("Successfully downloaded year %d → %s", year, out_file)
        return out_file

    except Exception as e:
        logger.error(
            "Failed to download GSOD for year %d after retries: %s",
            year,
            e,
            exc_info=True
        )
        return None
