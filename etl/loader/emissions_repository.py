# etl/loader/emissions_repository.py
import logging
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from typing import Any, Dict, List
from etl.config import ETLConfig

class EmissionsRepository:
    """Mongo operations on the `emissions` collection."""
    def __init__(self, cfg: ETLConfig, logger: logging.Logger) -> None:
        self.logger = logger.getChild(self.__class__.__name__)
        client = MongoClient(cfg.MONGODB_URI)
        self._col = client[cfg.DB_NAME]["emissions"]

    def count_for_year(self, year: int) -> int:
        """How many CO₂ docs do we already have for this calendar year?"""
        self.logger.debug(f"Counting CO₂ docs for {year}")
        cnt = self._col.count_documents({"year": year})
        self.logger.debug(f" → found {cnt}")
        return cnt

    def bulk_insert(self, docs: List[Dict[str, Any]]) -> None:
        """Insert many, ignoring duplicate‐key errors."""
        try:
            self._col.insert_many(docs, ordered=False)
        except BulkWriteError as bwe:
            errs = bwe.details.get("writeErrors", [])
            dupes = [e for e in errs if e["code"] == 11000]
            others = [e for e in errs if e["code"] != 11000]
            if dupes:
                self.logger.warning(f"Skipped {len(dupes)} duplicate CO₂ docs")
            if others:
                self.logger.error(f"{len(others)} other errors: {others}")
