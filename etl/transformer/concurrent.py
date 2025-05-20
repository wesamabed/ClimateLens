import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Mapping, Any, Optional

from .protocols import Transformer
from .parser import CsvParser
from .builder import PydanticRecordBuilder
from .reader import CsvReader

class ConcurrentTransformer(Transformer):
    """Run CsvReader.read across many files in parallel."""
    def __init__(self, max_workers: int=4,
                  chunk_size: int = 100,
                    logger: Optional[logging.Logger]=None,
                      use_processes: bool = False):
        self.max_workers = max_workers
        self.chunk_size  = chunk_size
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        parser = CsvParser(self.logger)
        builder = PydanticRecordBuilder(self.logger)
        self.reader = CsvReader(parser, builder, self.logger)
        self._use_processes = use_processes
        self._executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    def transform(self, paths: List[Path]) -> List[Mapping[str, Any]]:
        self.logger.info(f"Parallel transform: {len(paths)} files → chunks of {self.chunk_size}")
        # split into path‐lists of size chunk_size
        chunks = [
            paths[i : i + self.chunk_size]
            for i in range(0, len(paths), self.chunk_size)
        ]

        results: List[Mapping[str, Any]] = []
        with self._executor(
            max_workers=self.max_workers,
            thread_name_prefix=(
                "proc-transform" if self._executor is ProcessPoolExecutor
                else "thread-transform"
            )
        ) as exe:
            futures = {exe.submit(self._process_batch, c): c for c in chunks}
            for fut in as_completed(futures):
                batch = futures[fut]
                try:
                    results.extend(fut.result())
                except Exception as e:
                    self.logger.error(f"Batch { [p.name for p in batch] } failed: {e!r}")

        self.logger.info(f"Transformed total {len(results)} records")
        return results

    def _process_batch(self, paths: List[Path]) -> List[Mapping[str, Any]]:
        """
        Worker function (in its own thread or process).
        Re-create parser/builder/reader locally to avoid pickling loggers.
        """
        # local imports so that each process has its own instances
        from .parser import CsvParser
        from .builder import PydanticRecordBuilder
        from .reader import CsvReader
        if not self._use_processes:
            # Threads: reuse the shared reader
            local_reader = self.reader
        else:
            # Processes: build a fresh reader in this child process
            parser  = CsvParser(self.logger)
            builder = PydanticRecordBuilder(self.logger)
            local_reader  = CsvReader(parser, builder, self.logger)

        out: List[Mapping[str, Any]] = []
        for p in paths:
            try:
                out.extend(local_reader.read(p))
            except Exception as e:
                self.logger.error(f"{p.name} in batch failed: {e!r}")
        return out
