import logging
from pathlib import Path
from typing import List, Mapping, Any
from .protocols import Parser, RecordBuilder

class CsvReader:
    """Reads & validates every row; logs errors per row or per file."""
    def __init__(self, parser: Parser, builder: RecordBuilder, logger: logging.Logger):
        self.parser, self.builder = parser, builder
        self.logger = logger.getChild(self.__class__.__name__)

    def read(self, path: Path) -> List[Mapping[str, Any]]:
        self.logger.debug(f"Reading {path.name}")
        records: List[Mapping[str, Any]] = []
        try:
            with open(path, encoding="utf-8", newline="") as f:
                for raw in self.parser.parse(f):
                    try:
                        records.append(self.builder.build(raw))
                    except Exception as e:
                        self.logger.error(
                            f"{path.name} row validation failed: {e!r}",
                            extra={"raw": raw},
                        )
                        continue
        except Exception as e:
            self.logger.error(f"Could not open {path.name}: {e!r}")
        return records
