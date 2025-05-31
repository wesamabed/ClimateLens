# etl/embed/text_index.py

"""
Ensure both:
  • an Atlas Search text index (with synonyms) on climate.reports.text
  • a MongoDB 2dsphere index on weather.location
"""

from __future__ import annotations
import logging
from typing import List, Optional

import pymongo
import requests
from requests.auth import HTTPDigestAuth

JSON_HDR = {
    "Content-Type": "application/json",
    "Accept": "application/vnd.atlas.2024-05-30+json",
}


class AtlasTextIndexBuilder:
    """
    Idempotently:
      1. Upsert your synonyms under _id="co2_synonyms" in <db>.<synonyms_coll>
      2. Create an Atlas Search index named "reports_text" on <db>.reports.text
         using that synonyms collection
      3. Create a 2dsphere index on <db>.weather.location
    """

    def __init__(
        self,
        mongo_uri: str,
        proj_id: str,
        cluster: str,
        public_key: str,
        private_key: str,
        db_name: str = "climate",
        coll_name: str = "reports",
        synonyms_coll: str = "synonyms",
        synonyms: List[str] | None = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.mongo_uri     = mongo_uri
        self.db            = db_name
        self.coll          = coll_name
        self.synonyms_coll = synonyms_coll
        # default synonyms if none provided
        self.synonyms      = synonyms or [
            "co2", "carbon dioxide", "carbon-dioxide", "CO₂"
        ]

        # Atlas Admin API base
        self.base_url = (
            f"https://cloud.mongodb.com/api/atlas/v2/groups/{proj_id}"
            f"/clusters/{cluster}/search/indexes"
        )
        self.auth = HTTPDigestAuth(public_key, private_key)
        self.logger = (logger or logging.getLogger(__name__)).getChild(
            self.__class__.__name__
        )

    def _upsert_synonyms(self) -> None:
        """Ensure the synonyms document exists in Mongo."""
        self.logger.info("Upserting synonyms into %s.%s …", self.db, self.synonyms_coll)
        client = pymongo.MongoClient(self.mongo_uri)
        coll   = client[self.db][self.synonyms_coll]
        coll.update_one(
            {"_id": "co2_synonyms"},
            {"$set": {"values": self.synonyms}},
            upsert=True,
        )
        client.close()
        self.logger.info("Synonyms ready: %s", self.synonyms)

    def _current_indexes(self) -> list[dict]:
        """Fetch existing Search indexes for reports."""
        url  = f"{self.base_url}/{self.db}/{self.coll}"
        resp = requests.get(url, headers=JSON_HDR, auth=self.auth, timeout=30)
        if resp.status_code == 404:
            return []  # no search indexes yet
        resp.raise_for_status()
        return resp.json()

    def _index_spec(self) -> dict:
        """Build the JSON spec for the text index with synonyms."""
        return {
            "database":       self.db,
            "collectionName": self.coll,
            "name":           "reports_text",
            "type":           "search",
            "definition": {
                "analyzer": "lucene.standard",
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        # only index the `text` field for full-text
                        "text": { "type": "string" }
                    }
                },
                "synonyms": [
                    {
                        "name":     "co2_synonyms",
                        "analyzer": "lucene.standard",
                        "source":   { "collection": self.synonyms_coll },
                    }
                ],
            },
        }

    def _ensure_text_index(self) -> None:
        """Create the Atlas Search text index if missing."""
        try:
            existing = self._current_indexes()
        except Exception as e:
            self.logger.error("Failed to list existing text indexes: %s", e)
            return

        if any(ix.get("name") == "reports_text" for ix in existing):
            self.logger.info("Text index already present – skipping")
            return

        self.logger.info("Creating Atlas Search text index …")
        resp = requests.post(
            self.base_url,
            headers=JSON_HDR,
            auth=self.auth,
            json=self._index_spec(),
            timeout=30,
        )
        if resp.status_code == 409:
            self.logger.info("Text-index creation already in progress – OK")
            return
        if resp.status_code == 405:
            self.logger.warning(
                "Atlas returned 405 – Search may not be enabled on this tier."
            )
            return

        try:
            resp.raise_for_status()
        except Exception as e:
            self.logger.error("Text-index create failed: %s → %s", e, resp.text)
            return

        self.logger.info("Text index creation requested; may take a few minutes.")

