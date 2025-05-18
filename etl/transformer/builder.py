# etl/transformer/builder.py
import logging
from typing import Mapping, Any
from etl.transformer.converter import (
    ConverterRegistry,
    FahrenheitToCelsiusConverter,
    PressureConverter,
    VisibilityConverter,
    WindConverter,
    PrecipSnowConverter,
)
from etl.transformer.models import GSODRecord

class PydanticRecordBuilder:
    """
    1) Apply unit-conversion to every raw field via ConverterRegistry
    2) Delegate to Pydantic GSODRecord for schema validation & date parse
    """
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild(self.__class__.__name__)
        self.registry = ConverterRegistry([
            FahrenheitToCelsiusConverter(),
            PressureConverter(),
            VisibilityConverter(),
            WindConverter(),
            PrecipSnowConverter(),
        ])

    def build(self, raw: Mapping[str, str]) -> Mapping[str, Any]:
        # convert each raw value before validation
        converted: dict[str, Any] = {}
        for fld, val in raw.items():
            converted[fld] = self.registry.convert(fld, val)
        # now validate & parse dates via Pydantic
        rec = GSODRecord.model_validate(converted)
        return rec.model_dump()
