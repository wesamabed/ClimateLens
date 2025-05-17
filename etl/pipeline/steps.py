# etl/pipeline/steps.py
from abc import ABC, abstractmethod
from pathlib import Path
import csv
from typing import List, Dict
from etl.config import ETLConfig
from etl.downloader import download_year
from etl.logger import get_logger
from etl.models import GSODRecord

class ETLStep(ABC):
    """
    Strategy / Template Pattern:
    Each pipeline step implements `execute()`.
    """
    def __init__(self, config: ETLConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__, level="INFO")

    @abstractmethod
    def execute(self) -> None:
        ...

class DownloadStep(ETLStep):
    def execute(self) -> None:
        """Download GSOD for each year in the configured range."""
        for year in range(self.config.START_YEAR, self.config.END_YEAR + 1):
            path = download_year(year, Path(self.config.DATA_DIR))
            if path:
                self.logger.info("Downloaded year %d → %s", year, path)
            else:
                self.logger.warning("Skipped year %d after failures", year)

class TransformStep(ETLStep):
    def execute(self) -> List[Dict]:
        """
        1. Locate all gsod_*.csv under DATA_DIR
        2. For each file, stream rows via csv.DictReader
        3. Validate & transform via GSODRecord
        4. Collect JSON-ready dicts
        5. Log counts & skipped rows
        """
        results: List[Dict] = []
        base_dir = Path(self.config.DATA_DIR)
        self.logger.info("Scanning %s for CSVs", base_dir)

        for csv_file in base_dir.glob("gsod_*.csv"):
            self.logger.info("Transforming %s", csv_file.name)
            with open(csv_file, newline="") as fp:
                reader = csv.DictReader(fp)
                for idx, row in enumerate(reader, start=1):
                    try:
                        rec = GSODRecord(**row).model_dump()
                        results.append(rec)
                    except Exception as e:
                        self.logger.warning(
                            "Skipped bad row %d in %s: %s",
                            idx, csv_file.name, e
                        )

        self.logger.info("TransformStep: total records = %d", len(results))
        return results

class LoadStep(ETLStep):
    def execute(self) -> None:
        self.logger.info("LoadStep: not yet implemented")
