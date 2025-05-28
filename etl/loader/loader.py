# etl/loader/loader.py

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, Mapping, Any, Optional as optional

from .protocols import Loader, RecordPreparer, Repository

class BatchLoader(Loader):
    """
    Coordinates:
      - preparing each record via injected RecordPreparer
      - inserting via injected Repository
      - splitting into batches
      - optional concurrent execution
    """
    def __init__(
        self,
        preparer: RecordPreparer,
        repository: Repository,
        batch_size: int,
        max_workers: int,
        logger: logging.Logger,
        insert_fn: optional[callable] = None,
        retry_attempts: int = 3,
        retry_wait: int = 5,
    ):
        self.preparer      = preparer
        self.repository    = repository
        self.batch_size    = batch_size
        self.max_workers   = max_workers
        self.logger        = logger.getChild(self.__class__.__name__)
        self._insert_fn    = insert_fn or repository.bulk_insert
        self.retry_attempts= retry_attempts
        self.retry_wait    = retry_wait

    def load(self, records: Iterable[Mapping[str, Any]]) -> None:
        raw = list(records)
        total = len(raw)
        batches = [
            raw[i : i + self.batch_size]
            for i in range(0, total, self.batch_size)
        ]
        self.logger.info(f"Loading {total} docs in {len(batches)} batches")

        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="batch-loader") as exe:
            futures = {
                exe.submit(self._load_with_retry, idx + 1, batch): idx
                for idx, batch in enumerate(batches)
            }
            for fut in as_completed(futures):
                num = futures[fut] + 1
                try:
                    fut.result()
                except Exception as e:
                    self.logger.error(f"Batch {num} finally failed: {e!r}")
                else:
                    self.logger.info(f"Batch {num} done")
        self.logger.info("All batches complete")

    def _load_with_retry(self, batch_num: int, batch: list[Mapping[str, Any]]):
        attempts = 0
        while True:
            try:
                docs = [ self.preparer.prepare(r) for r in batch ]
                self._insert_fn(docs)
                return
            except Exception as e:
                attempts += 1
                self.logger.error(f"Batch {batch_num} attempt {attempts} error: {e!r}")
                if attempts >= self.retry_attempts:
                    raise
                time.sleep(self.retry_wait)
