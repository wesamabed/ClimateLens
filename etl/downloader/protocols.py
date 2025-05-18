from pathlib import Path
from typing import Iterable, List, Protocol
import ftplib

class Downloader(Protocol):
    def download_year_tar(self, year: int, dest_dir: Path) -> Path:
        ...

    def download_years(self, years: Iterable[int], dest_dir: Path, max_workers: int = 4) -> List[Path]:
        ...

class FTPClientInterface(Protocol):
    def login_and_cwd(self, host: str, user: str, passwd: str, year: int) -> ftplib.FTP:
        ...

class ArchiveExtractor(Protocol):
    """
    Protocol for archive extraction functionality.
    """
    def extract(self, archive_path: Path, dest_dir: Path) -> List[Path]:
        ...