# etl/loader/repository.py

import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from typing import Any, Dict, List
from etl.config import ETLConfig

class MongoRepository:
    """Handles all direct MongoDB operations."""
    def __init__(self, cfg: ETLConfig, logger: logging.Logger) -> None:
        self.logger = logger.getChild(self.__class__.__name__)
        self._client = MongoClient(cfg.MONGODB_URI)
        self._col = self._client[cfg.DB_NAME]["weather"]

    def count_for_year(self, year: int) -> int:
        """
        Return how many documents we already have for a given calendar year.
        We treat any doc whose `record_date` is ≥ Jan 1 of that year
        and < Jan 1 of the next year as “in that year.”
        """
        start = datetime(year, 1, 1)
        end   = datetime(year + 1, 1, 1)
        self.logger.debug(f"Counting docs for {year}: {start!r}→{end!r}")
        cnt = self._col.count_documents({
            "record_date": {"$gte": start, "$lt": end}
        })
        self.logger.debug(f"Found {cnt} docs for year {year}")
        return cnt
    
    def bulk_insert(self, docs: List[Dict[str, Any]]) -> None:
        try:
            self._col.insert_many(docs, ordered=False)
        except BulkWriteError as bwe:
            # split out duplicate-key vs others
            errs = bwe.details.get("writeErrors", [])
            dups = [e for e in errs if e["code"] == 11000]
            others = [e for e in errs if e["code"] != 11000]
            if dups:
                self.logger.warning(f"Skipped {len(dups)} duplicates.")
            if others:
                self.logger.error(f"{len(others)} non-duplicate errors: {others}")
