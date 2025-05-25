# etl/pipeline/co2_download_step.py
import logging
import time
from typing import Iterable, List, Mapping, Any, Optional

from etl.pipeline.protocols import Step
from etl.config import ETLConfig
from etl.downloader.co2_downloader import CO2Downloader

class CO2DownloadStep(Step[Iterable[int], List[Mapping[str,Any]]]):
    """
    Wraps a CO2Downloader so that it can be used in our Pipeline.
    Input: iterable of years
    Output: list of raw JSON records from the World Bank API
    """
    def __init__(
        self,
        config: ETLConfig,
        downloader: CO2Downloader,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.config     = config
        self.downloader = downloader
        base = logger or logging.getLogger(__name__)
        self.logger     = base.getChild(self.__class__.__name__)

    def execute(self, years: Optional[Iterable[int]] = None) -> List[Mapping[str,Any]]:
        # determine which years to fetch
        if years is None:
            years = range(self.config.CO2_START_YEAR, self.config.CO2_END_YEAR + 1)
        years = sorted(set(years))
        self.logger.info(
            "Starting CO₂ download: indicator=%s, years=%s",
            self.downloader.indicator, years
        )

        # time the fetch
        start_ts = time.perf_counter()
        try:
            records = self.downloader.download_years(years=years)
        except Exception as e:
            self.logger.error(
                "CO₂ download failed after %.2f sec for years %s: %s",
                time.perf_counter() - start_ts, years, e, exc_info=True
            )
            raise
        elapsed = time.perf_counter() - start_ts

        # summary logging
        count = len(records) if records is not None else 0
        self.logger.info(
            "Completed CO₂ download: %d records in %.2f sec", count, elapsed
        )
        if count:
            # log a small sample for sanity
            sample = records[0]
            self.logger.debug("Sample record keys: %s", list(sample.keys()))
            self.logger.debug("Sample record: %s", sample)

        return records
