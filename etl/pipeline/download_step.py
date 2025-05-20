# etl/pipeline/download_step.py
from pathlib import Path
from typing import List, Iterable, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from etl.downloader.protocols import Downloader, ArchiveExtractor
from etl.config import ETLConfig
from etl.pipeline.protocols import Step

class DownloadStep(Step[Iterable[int], List[Path]]):
    def __init__(
        self,
        config: ETLConfig,
        downloader: Downloader,
        extractor: ArchiveExtractor,
        logger: logging.Logger,
    ):
        self.config     = config
        self.downloader = downloader
        self.extractor  = extractor
        self.logger     = logger.getChild(self.__class__.__name__)

    def execute(self, years: Optional[Iterable[int]] = None) -> List[Path]:
        # if no explicit years list provided, use the full config range
        if years is None:
            years = range(self.config.START_YEAR, self.config.END_YEAR + 1)
        years = list(years)
        self.logger.info(f"Downloading years {years}")
        
        raw_dir = self.config.DATA_DIR / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)

        archives = self.downloader.download_years(
            years=years,
            dest_dir=raw_dir,
            max_workers=self.config.DOWNLOAD_MAX_WORKERS,
        )
        all_csv: List[Path] = []
        with ThreadPoolExecutor(
            max_workers=self.config.DOWNLOAD_MAX_WORKERS,
            thread_name_prefix="tar-extract"
        ) as exe:
            futures = {}
            for arch in archives:
                year_dir_name = Path(arch.name).name.split(".", 1)[0]
                dest = self.config.DATA_DIR / year_dir_name
                futures[exe.submit(self.extractor.extract, arch, dest)] = arch
            # as each extraction finishes, collect its CSVs
            for fut in as_completed(futures):
                archive = futures[fut]
                try:
                    csvs = fut.result()
                    all_csv.extend(csvs)
                except Exception as e:
                    self.logger.error(f"Extraction of {archive.name} failed: {e!r}")
                return all_csv