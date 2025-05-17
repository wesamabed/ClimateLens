# etl/pipeline/steps.py
from abc import ABC, abstractmethod
from pathlib import Path
from etl.config import ETLConfig
from etl.downloader import download_year
from etl.logger import get_logger

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
    def execute(self) -> None:
        self.logger.info("TransformStep: not yet implemented")

class LoadStep(ETLStep):
    def execute(self) -> None:
        self.logger.info("LoadStep: not yet implemented")
