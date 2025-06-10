"""
etl/embed/synonyms_loader.py
—————————————
Rebuilds <DB>.<SYNONYMS_COLL> with Atlas v2-valid documents.

Required fields per Atlas docs:
  • mappingType   ("equivalent" | "explicit")
  • synonyms      [str, …]         (always)
  • input         [str, …]         (only for explicit)

The loader:
  ▸ Drops old docs (easiest way to remove invalid ones)
  ▸ Inserts
        – generic “equivalent” sets   (airport ↔ apt, etc.)
        – climate acronyms            (co2, ghg, …)
        – ISO-3 ⇆ country docs        (explicit mapping, auto-generated)
Safe to call repeatedly.
"""
from typing import List, Optional
import logging

from pymongo import MongoClient
from etl.config import ETLConfig


# ────────────────────────────────────────────────────────────────────
def _iso3_docs(db, log) -> List[dict]:
    """Return explicit mapping docs built from emissions collection."""
    out: List[dict] = []
    for d in db.emissions.find({}, {"iso3": 1, "country": 1}):
        iso = d.get("iso3", "").lower()
        cty = d.get("country", "").lower()
        if iso and cty:
            out.append({
                "mappingType": "explicit",
                "input": [iso],
                "synonyms": [cty]
            })
            out.append({
                "mappingType": "explicit",
                "input": [cty],
                "synonyms": [iso]
            })
    log.info("Generated %s ISO-3 synonym docs", len(out))
    return out


# ────────────────────────────────────────────────────────────────────
class SynonymsLoader:
    def __init__(self, cfg: ETLConfig, logger: Optional[logging.Logger] = None):
        self.cfg    = cfg
        self.logger = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)
        self.db     = MongoClient(cfg.MONGODB_URI)[cfg.DB_NAME]
        self.coll   = self.db[getattr(cfg, "SYNONYMS_COLL", "synonyms")]

    # ---------------- main entry ----------------
    def load(self) -> None:
        self.logger.info("Recreating %s.%s", self.db.name, self.coll.name)
        self.coll.delete_many({})                           # nuke invalid docs

        docs: List[dict] = [
            # — generic place abbreviations —
            {"mappingType": "equivalent",
             "synonyms": ["airport", "apt", "airpt", "aerodrome"]},
            {"mappingType": "equivalent",
             "synonyms": ["international", "intl"]},
            {"mappingType": "equivalent",
             "synonyms": ["station", "stn"]},
            {"mappingType": "equivalent",
             "synonyms": ["north", "n"]},
            {"mappingType": "equivalent",
             "synonyms": ["south", "s"]},
            {"mappingType": "equivalent",
             "synonyms": ["east",  "e"]},
            {"mappingType": "equivalent",
             "synonyms": ["west",  "w"]},

            # — climate acronyms —
            {"mappingType": "equivalent",
             "synonyms": ["co2", "co₂", "carbon dioxide"]},
            {"mappingType": "equivalent",
             "synonyms": ["ghg", "greenhouse gas"]},
        ] + _iso3_docs(self.db, self.logger)

        if docs:
            self.coll.insert_many(docs, ordered=False)
            self.logger.info("Inserted %s synonym docs", len(docs))
        else:
            self.logger.warning("No synonym docs generated.")
