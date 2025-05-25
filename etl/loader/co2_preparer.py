# etl/loader/co2_preparer.py
from typing import Mapping, Any
from etl.loader.protocols import RecordPreparer

class CO2RecordPreparer(RecordPreparer):
    def __init__(self, logger=None):
        self.logger = logger

    def prepare(self, rec: Mapping[str,Any]) -> Mapping[str,Any]:
        return rec
