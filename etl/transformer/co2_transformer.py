import logging
from typing import List, Mapping, Any

from etl.transformer.protocols import Transformer

class CO2Transformer(Transformer):
    """
    Turn raw World Bank JSON records into flat Mongo docs:
      { country, iso3, year, co2Mt }
    Robustly skips malformed or missing‐value records, logging each.
    """
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def transform(self, records: List[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        total = len(records)
        self.logger.debug(f"Starting CO₂ transform for {total} raw records")
        out: List[Mapping[str, Any]] = []
        skipped = 0

        for idx, rec in enumerate(records, start=1):
            try:
                # required fields
                country = rec.get("country", {}).get("value")
                iso3    = rec.get("countryiso3code")
                date_str= rec.get("date")
                value   = rec.get("value")

                # check presence
                if country is None or iso3 is None or date_str is None:
                    raise KeyError("missing country / iso3 / date")

                # skip empty data
                if value is None:
                    self.logger.debug(f"[{idx}/{total}] no value → skipping")
                    skipped += 1
                    continue

                # cast types
                year  = int(date_str)
                co2Mt = float(value)

                out.append({
                    "country": country,
                    "iso3":     iso3,
                    "year":     year,
                    "co2Mt":    co2Mt,
                })

            except Exception as exc:
                skipped += 1
                # include the record index so you can trace back easily
                self.logger.warning(
                    f"[{idx}/{total}] skipping bad record: {exc!r}; record={rec!r}"
                )

        kept = len(out)
        self.logger.info(f"CO₂ transform complete: kept {kept}/{total}, skipped {skipped}")
        return out
