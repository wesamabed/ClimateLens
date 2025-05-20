# etl/downloader/tar_extractor.py
import logging
import tarfile
import time
from pathlib import Path
from typing import List, Optional

from etl.downloader.protocols import ArchiveExtractor

class TarExtractor(ArchiveExtractor):
    """
    Extracts only `.csv` files from a (possibly gzipped) tar archive.
    Prevents path traversal and logs progress.
    """
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def extract(self, archive_path: Path, dest_dir: Path) -> List[Path]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        extracted: List[Path] = []
        self.logger.info(f"Extracting {archive_path.name} → {dest_dir}")
        t0 = time.perf_counter()

        def safe(member, target_dir: Path) -> bool:
            target = (target_dir / Path(member.name).name).resolve()
            return str(target).startswith(str(target_dir.resolve()))

        with tarfile.open(archive_path, mode="r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile() or not member.name.lower().endswith(".csv"):
                    continue
                filename = Path(member.name).name
                target = dest_dir / filename
                if not safe(member, dest_dir):
                    self.logger.warning("Skipping unsafe path %s", member.name)
                    continue
                src = tf.extractfile(member)
                if not src:
                    self.logger.error("Failed to read %s", member.name)
                    continue
                with open(target, "wb") as out:
                    out.write(src.read())
                extracted.append(target)

        elapsed = time.perf_counter() - t0
        self.logger.info(f"Extracted {len(extracted)} CSV files in {elapsed:.1f}s")
        return extracted

    # alias for backward‐compatibility
    def extract_csv(self, archive_path: Path, dest_dir: Path) -> List[Path]:
        return self.extract(archive_path, dest_dir)
