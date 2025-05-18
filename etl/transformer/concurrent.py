# etl/transformer/concurrent.py
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Mapping, Optional, Any

from etl.transformer.protocols import Transformer
from etl.transformer.parser import FixedWidthParser
from etl.transformer.builder import PydanticRecordBuilder
from etl.transformer.reader import OpGzReader

class ConcurrentTransformer(Transformer):
    """
    Strategy: concurrent, file-by-file transform.
    """
    def __init__(self, max_workers: int = 4, logger: Optional[logging.Logger] = None):
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        # inject our parsing & building strategies
        self.parser  = FixedWidthParser(self.logger)
        self.builder = PydanticRecordBuilder(self.logger)
        self.reader  = OpGzReader(self.parser, self.builder, self.logger)

    def transform(self, paths: List[Path]) -> List[Mapping[str, Any]]:
        paths = list(paths)
        self.logger.info(f"Parallel transform of {len(paths)} files")
        out: List[Mapping[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as exe:
            futures = {exe.submit(self.reader.read, p): p for p in paths}
            for fut in as_completed(futures):
                p = futures[fut]
                try:
                    batch = fut.result()
                    out.extend(batch)
                except Exception as e:
                    self.logger.error(f"✖ Failed transforming {p.name}: {e!r}")
        self.logger.info(f"Transformed total {len(out)} records")
        return out
