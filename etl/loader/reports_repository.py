# etl/loader/reports_repository.py
import logging
from typing import Any, Dict, List

from pymongo import MongoClient, UpdateOne
import pymongo
from pymongo.errors import OperationFailure

from etl.config import ETLConfig


class ReportsRepository:
    """Upsert IPCC report chunks; unique on (section, paragraph)."""

    def __init__(self, cfg: ETLConfig, logger: logging.Logger) -> None:
        self.logger = logger.getChild(self.__class__.__name__)
        client      = MongoClient(cfg.MONGODB_URI)
        db          = client[cfg.DB_NAME]
        self.col    = db["reports"]

        # Ensure unique compound index, but swallow “already exists” clash
        try:
            self.col.create_index(
                [("section", 1), ("paragraph", 1)],
                unique=True,
                name="uix_section_paragraph",
            )
        except OperationFailure as e:
            if e.code == 85:          # IndexOptionsConflict
                self.logger.debug("Index already present – skip create_index()")
            else:
                raise

    # ------------------------------------------------------------------ #
    # BatchLoader looks for bulk_insert; we alias to bulk_upsert for clarity
    # ------------------------------------------------------------------ #
    def bulk_insert(self, docs: List[Dict[str, Any]]) -> None:
        """Alias expected by BatchLoader → just call bulk_upsert."""
        self.bulk_upsert(docs)

    # real work --------------------------------------------------------- #
    def bulk_upsert(self, docs: List[Dict[str, Any]]) -> None:
        if not docs:
            return
        ops = [
            UpdateOne(
                {"section": d["section"], "paragraph": d["paragraph"]},
                {"$setOnInsert": d},
                upsert=True,
            )
            for d in docs
        ]
        result = self.col.bulk_write(ops, ordered=False)
        self.logger.info(
            "Reports upserted: ins=%d matched=%d modified=%d",
            result.upserted_count,
            result.matched_count,
            result.modified_count,
        )

    def bulk_upsert_embeddings(self, docs: List[Dict[str, Any]]) -> None:
        """
        Upsert {section, paragraph} and add / update 'embedding'.
        """
        if not docs:
            return

        ops = [
            pymongo.UpdateOne(
                {"section": d["section"], "paragraph": d["paragraph"]},
                {"$set": {"embedding": d["embedding"]}},
                upsert=False,   # assume base doc exists – skip silently otherwise
            )
            for d in docs
        ]
        res = self.col.bulk_write(ops, ordered=False)
        self.logger.info(
            f"Embeddings upserted: matched={res.matched_count} "
            f"modified={res.modified_count}"
        )