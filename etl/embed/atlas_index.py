# etl/embed/atlas_index.py
"""
Ensure a Vector Search index called `reports_embedding`
exists on climate.reports.embedding (HNSW, cosine).
"""

from __future__ import annotations
import json, logging
from typing import Optional
import requests
from requests.auth import HTTPDigestAuth

JSON_HDR = {"Content-Type": "application/json", "Accept": "application/vnd.atlas.2024-05-30+json"}


class AtlasIndexBuilder:
    def __init__(
        self,
        proj_id: str,
        cluster: str,
        public_key: str,
        private_key: str,
        db_name: str = "climate",
        coll_name: str = "reports",
        dim: int = 3072,
        logger: Optional[logging.Logger] = None,
    ):
        self.project, self.cluster = proj_id, cluster
        self.db, self.coll, self.dim = db_name, coll_name, dim
        self.auth = HTTPDigestAuth(public_key, private_key)
        self.logger = (logger or logging.getLogger(__name__)).getChild(
            self.__class__.__name__
        )

        # Base Search-API root for this cluster
        self.base = (
            f"https://cloud.mongodb.com/api/atlas/v2/groups/{self.project}"
            f"/clusters/{self.cluster}/search/indexes"
        )

    # ---------- helpers --------------------------------------------------
    def _current_indexes(self) -> list[dict]:
        url = f"{self.base}/{self.db}/{self.coll}"
        r = requests.get(url, headers=JSON_HDR, auth=self.auth, timeout=30)
        if r.status_code == 404:   # collection has no search indexes yet
            return []
        if r.status_code == 401:
            raise RuntimeError("API key unauthorised – check project roles/IP list")
        r.raise_for_status()
        return r.json()

    def _spec(self) -> dict:
        return {
            "database": self.db,
            "collectionName": self.coll,
            "name": "reports_embedding",
            "type": "vectorSearch",
            "definition": {                       
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": self.dim,
                        "similarity": "cosine"
                    }
                ]
            }
        }

    # ---------- public ---------------------------------------------------
    def ensure(self) -> None:
        self.logger.info("Ensuring Atlas Vector Search index")
        try:
            if any(ix.get("name") == "reports_embedding" for ix in self._current_indexes()):
                self.logger.info("Vector index already present – skipping")
                return
        except Exception as exc:
            self.logger.error(f"Index list failed: {exc}")
            return

        # POST goes to cluster-level endpoint (no /db/coll suffix)
        resp = requests.post(
            self.base, headers=JSON_HDR, auth=self.auth, json=self._spec(), timeout=30
        )

        if resp.status_code == 405:
            self.logger.warning(
                "Atlas returned 405 – Is Search enabled on the cluster? "
                "Ensure the cluster is M10+ and Search is not disabled."
            )
            return
        if resp.status_code == 409:
            self.logger.info("Index creation already in progress – OK")
            return
        try:
            resp.raise_for_status()
        except Exception as exc:
            self.logger.error(f"Index create failed: {exc} → {resp.text}")
            return

        self.logger.info("Vector index creation requested – it may take a minute to build.")
