import logging
from datetime import date
from etl.loader.preparer import DefaultRecordPreparer

def test_prepare_fields():
    logger = logging.getLogger("test_prepader_builder")
    logger.setLevel(logging.DEBUG)
    prep = DefaultRecordPreparer(logger)
    raw = {"station":"S1", "record_date": date(2020,1,2), "other": 5}
    out = prep.prepare(raw)
    assert out["stationId"] == "S1"
    assert isinstance(out["recordDate"], __import__("datetime").datetime)
    assert out["other"] == 5
