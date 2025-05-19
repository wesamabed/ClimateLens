# etl/transformer/protocols.py
from pathlib import Path
from typing import Iterator, Mapping, Any, List, Protocol

class Parser(Protocol):
    """Split raw text → sequence of raw rows (dict[str,str])."""
    def parse(self, lines: Iterator[str]) -> Iterator[Mapping[str, str]]:
        ...

class RecordBuilder(Protocol):
    """Validate & type-cast one raw row → rich dict[str,Any]."""
    def build(self, raw: Mapping[str, str]) -> Mapping[str, Any]:
        ...

class Transformer(Protocol):
    """Take many file-paths → flat list of rich dicts."""
    def transform(self, paths: List[Path]) -> List[Mapping[str, Any]]:
        ...
