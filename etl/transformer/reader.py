# etl/transformer/reader.py
import gzip
import logging
from pathlib import Path
from typing import List, Mapping, Any
from etl.transformer.protocols import Parser, RecordBuilder

class OpGzReader:
    """
    Knows how to read a single `.op.gz` GSOD file,
    parse it via FixedWidthParser and validate via PydanticRecordBuilder.
    """
    def __init__(
        self,
        parser: Parser,
        builder: RecordBuilder,
        logger: logging.Logger
    ) -> None:
        self.parser  = parser
        self.builder = builder
        self.logger  = logger.getChild(self.__class__.__name__)

    def read(self, path: Path) -> List[Mapping[str, Any]]:
        self.logger.debug(f"Reading {path.name}")
        out: List[Mapping[str, Any]] = []
        try:
            with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
                # skip blank lines until header
                data = (line for line in f if line.strip())
                for raw in self.parser.parse(data):
                    try:
                        rec = self.builder.build(raw)
                        out.append(rec)
                    except Exception:
                        # already logged inside builder
                        continue
        except Exception as e:
            self.logger.error(f"Could not read {path.name}: {e!r}")
        return out
