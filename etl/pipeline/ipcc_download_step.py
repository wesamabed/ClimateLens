from typing import List, Optional, Iterable
import logging
import pathlib
from etl.pipeline.protocols import Step
from etl.config import ETLConfig
from etl.downloader.pdf_downloader import PDFDownloader

class IPCCDownloadStep(Step[Iterable[int], List[pathlib.Path]]):
    """Just returns [Path(pdf)] so the next step receives the file path."""
    def __init__(
        self,
        cfg: ETLConfig,
        downloader: PDFDownloader,
        logger: Optional[logging.Logger] = None
    ):
        self.cfg, self.dl = cfg, downloader
        self.logger = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)

    def execute(self, _: Optional[Iterable[int]] = None) -> List[pathlib.Path]:   # years arg unused
        return self.dl.download_years()
