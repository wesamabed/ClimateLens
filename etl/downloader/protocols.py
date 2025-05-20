# etl/downloader/protocols.py
from pathlib import Path
from typing import Iterable, List, Protocol

class Downloader(Protocol):
    """
    Fetches per‐year archive files (e.g. .tar.gz) into a local folder.
    """
    def download_year_tar(self, year: int, dest_dir: Path) -> Path:
        ...
    def download_years(
        self,
        years: Iterable[int],
        dest_dir: Path,
        max_workers: int = 4
    ) -> List[Path]:
        ...

class ArchiveExtractor(Protocol):
    """
    Unpacks a (possibly compressed) tar archive into a destination folder.
    """
    def extract(self, archive_path: Path, dest_dir: Path) -> List[Path]:
        ...
