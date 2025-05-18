# etl/loader/protocols.py

from typing import Protocol, Iterable, Any, Mapping

class RecordPreparer(Protocol):
    """Transform one raw record → ready-to-insert dict."""
    def prepare(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        ...

class Repository(Protocol):
    """Abstract persistent store for prepared records."""
    def bulk_insert(self, docs: list[dict[str, Any]]) -> None:
        ...

class Loader(Protocol):
    """High-level ETL loader orchestration."""
    def load(self, records: Iterable[Mapping[str, Any]]) -> None:
        ...
