# etl/loader/identity_preparer.py
from typing import Mapping, Any
from etl.loader.protocols import RecordPreparer

class IdentityPreparer(RecordPreparer):
    def __init__(self, logger=None):
        self.logger = logger

    def prepare(self, rec: Mapping[str,Any]) -> Mapping[str,Any]:
        return rec
