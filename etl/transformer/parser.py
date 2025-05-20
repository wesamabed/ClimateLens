import csv
import logging
from typing import Iterator, Mapping, TextIO, Optional
from .protocols import Parser

class CsvParser(Parser):
    """Reads comma-quoted CSV rows and splits the FRSHTT flags."""
    def __init__(self, logger: Optional[logging.Logger]=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def parse(self, f: TextIO) -> Iterator[Mapping[str, str]]:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=1):
            try:
                bits = (row.get("FRSHTT") or "").strip()
                flags = [bit=="1" for bit in bits] if bits.isdigit() and len(bits)==6 else [False]*6
                for name, val in zip(
                    ("fog","rain","snow","hail","thunder","tornado"), flags
                ):
                    row[f"frshtt_{name}"] = val
                yield row
            except Exception as e:
                self.logger.warning(f"Line {lineno} parse error: {e!r} → {row}")
                continue
