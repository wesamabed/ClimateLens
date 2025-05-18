# etl/pipeline/protocols.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")

class Step(ABC, Generic[T, R]):
    """
    A pipeline Step consumes input T and returns output R.
    """
    @abstractmethod
    def execute(self, data: T) -> R:
        ...
