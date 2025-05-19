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
        if "station_id" in rec:
            rec["stationId"] = rec.pop("station_id")
        for key in ("date", "record_date"):
            d = rec.get(key)
            if isinstance(d, date) and not isinstance(d, datetime):
                rec[key] = datetime.combine(d, time.min)
        return rec
