import logging
from typing import Dict, List, Optional

import requests
from pymongo import MongoClient
from requests.auth import HTTPDigestAuth

JSON_HDR = {
    "Content-Type": "application/json",
    "Accept": "application/vnd.atlas.2024-05-30+json",
}


class IndexCreator:
    """Creates all B-tree and Atlas-Search indexes for ClimateLens."""

    # ──────────────────────────────────────────────
    def __init__(
        self,
        mongodb_uri: str,
        atlas_project_id: str,
        atlas_cluster: str,
        atlas_public_key: str,
        atlas_private_key: str,
        db_name: str,
        synonyms_coll: str,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)
        self._db    = MongoClient(mongodb_uri)[db_name]
        self._auth  = HTTPDigestAuth(atlas_public_key, atlas_private_key)
        self._base  = (
            f"https://cloud.mongodb.com/api/atlas/v2/groups/{atlas_project_id}"
            f"/clusters/{atlas_cluster}/search/indexes"
        )
        self._syn = synonyms_coll

    # ──────────────────────────────────────────────
    # 1. Mongo B-tree / geo / partial indexes
    # ──────────────────────────────────────────────
    def create_btree_indexes(self) -> None:
        w = self._db["weather"]
        self._ensure(w, [("stationId", 1)])
        self._ensure(w, [("recordDate", 1)])
        self._ensure(w, [("location", "2dsphere"), ("recordDate", 1)],
                     name="location_date", geo=True)
        self._ensure(w, [("stationId", 1), ("recordDate", 1)], name="station_date")
        self._ensure(w, [("recordDate", 1), ("temp", -1), ("max_temp", -1)],
                     name="date_temp")
        self._ensure_partial(
            w, [("frshtt_fog", 1), ("recordDate", 1), ("stationId", 1)],
            {"frshtt_fog": True}, "fog_date_station")
        self._ensure_partial(
            w, [("frshtt_rain", 1), ("recordDate", 1), ("stationId", 1)],
            {"frshtt_rain": True}, "rain_date_station")
        self._ensure(w, [("location", "2dsphere")], geo=True)
        self.logger.info("Weather B-tree indexes ensured.")

        e = self._db["emissions"]
        self._ensure(e, [("iso3", 1)])
        self._ensure(e, [("country", 1)])
        self._ensure(e, [("year", 1)])
        self._ensure(e, [("iso3", 1), ("year", 1)], name="iso3_year")
        self.logger.info("Emissions B-tree indexes ensured.")

    # ──────────────────────────────────────────────
    # 2. Atlas Search indexes
    # ──────────────────────────────────────────────
    def ensure_atlas_search_indexes(self) -> None:
        self._ensure_search(self._weather_spec(),   "weather_text")
        self._ensure_search(self._emissions_spec(), "emissions_search")

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────
    def _ensure(self, coll, keys: List[tuple], name=None, geo=False, **kw):
        name = name or "_".join(
            f"{k}_{'2dsphere' if geo and v=='2dsphere' else v}" for k, v in keys
        )
        if name not in {ix["name"] for ix in coll.list_indexes()}:
            coll.create_index(keys, name=name, **kw)
            self.logger.debug("→ created %s", name)

    def _ensure_partial(self, coll, keys, pfe, name):
        if name not in {ix["name"] for ix in coll.list_indexes()}:
            coll.create_index(keys, name=name, partialFilterExpression=pfe, background=True)
            self.logger.debug("→ created %s", name)

    def _exists(self, db, coll, ix_name) -> bool:
        url = f"{self._base}/{db}/{coll}"
        r   = requests.get(url, headers=JSON_HDR, auth=self._auth, timeout=30)
        return any(ix.get("name") == ix_name for ix in r.json() or [])

    def _ensure_search(self, spec: Dict, ix_name: str):
        if self._exists(spec["database"], spec["collectionName"], ix_name):
            self.logger.info("Atlas index '%s' already exists.", ix_name)
            return
        requests.post(self._base, headers=JSON_HDR, auth=self._auth,
                      json=spec, timeout=30).raise_for_status()
        self.logger.info("Atlas index '%s' ensured.", ix_name)

    # ──────────────────────────────────────────────
    # JSON specs
    # ──────────────────────────────────────────────
    def _weather_spec(self) -> Dict:
        return {
            "database": "climate",
            "collectionName": "weather",
            "name": "weather_text",
            "type": "search",
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "name": {
                            "type": "string",
                            "analyzer": "weather_name_analyzer"
                        }
                    }
                },
                "analyzers": [
                    {
                        "name": "weather_name_analyzer",
                        "tokenizer": {"type": "standard"},
                        "charFilters": [],
                        "tokenFilters": [
                            {"type": "lowercase"},
                            {"type": "asciiFolding"},
                            {"type": "edgeGram", "minGram": 3, "maxGram": 20}
                        ]
                    }
                ],
                "synonyms": [
                    {
                        "name": "generic_words",
                        "analyzer": "lucene.standard",
                        "source": {"collection": self._syn}
                    }
                ]
            }
        }

    def _emissions_spec(self) -> Dict:
        return {
            "database": "climate",
            "collectionName": "emissions",
            "name": "emissions_search",
            "type": "search",
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "country": { "type": "string", "analyzer": "lucene.standard" },
                        "iso3":    { "type": "string" }
                    }
                },
                "synonyms": [
                    {
                        "name": "generic_words",
                        "analyzer": "lucene.standard",
                        "source": {"collection": self._syn}
                    }
                ]
            }
        }
