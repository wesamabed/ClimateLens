# etl/loader/preparer.py

import logging
from datetime import date, datetime, time
from typing import Any, Mapping

class DefaultRecordPreparer:
    """Rename fields and normalize dates."""
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild(self.__class__.__name__)

    def prepare(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        rec = dict(raw)  # shallow copy
        if "station" in rec:
            rec["stationId"] = rec.pop("station")
        if "record_date" in rec and isinstance(rec["record_date"], date):
            dt = rec.pop("record_date")
            rec["recordDate"] = datetime.combine(dt, time.min)
        lat = rec.pop("latitude", None)
        lon = rec.pop("longitude", None)
        if lat is not None and lon is not None:
            # MongoDB expects [longitude, latitude]
            rec["location"] = {"type": "Point", "coordinates": [lon, lat]}
        return rec
