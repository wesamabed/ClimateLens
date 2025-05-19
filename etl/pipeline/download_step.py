# etl/pipeline/download_step.py
from pathlib import Path
from typing import List, Iterable, Optional
import logging

from etl.config import ETLConfig
from etl.downloader.protocols import Downloader
from etl.downloader.tar_extractor import TarExtractor
from etl.pipeline.protocols import Step

class DownloadStep(Step[None, List[Path]]):
    def __init__(
        self,
        config: ETLConfig,
        downloader: Downloader,
        extractor: TarExtractor,
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

        tar_paths = self.downloader.download_years(
            years=years,
            dest_dir=raw_dir,
            max_workers=self.config.FTP_MAX_WORKERS,
        )

        all_op: List[Path] = []
        for tar in tar_paths:
            year_str = tar.stem.split("_", 1)[1]
            year_dir = self.config.DATA_DIR / year_str
            op_files = self.extractor.extract_op_gz(tar, year_dir)
            all_op.extend(op_files)

        self.logger.info(f"DownloadStep: {len(all_op)} files ready")
        return all_op
