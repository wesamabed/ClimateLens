from __future__ import annotations

import logging
import tarfile
import time
from pathlib import Path
from typing import List, Optional

from etl.downloader.protocols import ArchiveExtractor

class TarExtractor(ArchiveExtractor):
    """
    Extract only `.op.gz` members from a .tar archive into a destination folder.
    
    This extractor applies:
      - Single Responsibility: only extracts .op.gz files.
      - Security: prevents path traversal by resolving the destination.
      - Dependency Injection: accepts a custom logger.
    """
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def extract(self, tar_path: Path, dest_dir: Path) -> List[Path]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        extracted_files: List[Path] = []
        self.logger.info("Extracting from %s into %s", tar_path.name, dest_dir)
        t0 = time.perf_counter()

        def is_within_directory(directory: Path, target: Path) -> bool:
            try:
                directory = directory.resolve(strict=False)
                target = target.resolve(strict=False)
                return str(target).startswith(str(directory))
            except Exception:
                return False

        with tarfile.open(tar_path, mode="r") as tf:
            for member in tf.getmembers():
                # Check that the member is a file and ends with .op.gz
                if not member.isfile() or not member.name.endswith(".op.gz"):
                    continue
                # Use only the file name to avoid nested paths
                filename = Path(member.name).name  
                target = dest_dir / filename

                # Security check: Ensure the target is within dest_dir
                if not is_within_directory(dest_dir, target):
                    self.logger.warning("Skipping extraction for %s due to unsafe path", member.name)
                    continue

                self.logger.debug("  ↳ %s", filename)
                src = tf.extractfile(member)
                if src is None:
                    self.logger.error("Failed to extract %s", member.name)
                    continue
                with open(target, "wb") as dst:
                    dst.write(src.read())
                extracted_files.append(target)

        self.logger.info("Extracted %d files in %.1f s", len(extracted_files), time.perf_counter() - t0)
        return extracted_files

    def extract_op_gz(self, tar_path: Path, dest_dir: Path) -> List[Path]:
        """
        Alias method to support tests expecting extract_op_gz.
        """
        return self.extract(tar_path, dest_dir)