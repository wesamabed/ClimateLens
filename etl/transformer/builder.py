import logging
from typing import Mapping, Any, Dict
from .converter import (
    FloatConverter,
    AttributesConverter,
    ConverterRegistry,
    FahrenheitToCelsiusConverter,
    PressureConverter,
    VisibilityConverter,
    WindConverter,
    PrecipSnowConverter,
)
from .models import GSODRecord

class PydanticRecordBuilder:
    """
    1) Normalize & convert raw fields via ConverterRegistry.
    2) Validate & coerce with Pydantic GSODRecord.
    """
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild(self.__class__.__name__)
        self.registry = ConverterRegistry([
            FloatConverter(),
            AttributesConverter(),
            FahrenheitToCelsiusConverter(),
            PressureConverter(),
            VisibilityConverter(),
            WindConverter(),
            PrecipSnowConverter(),
        ])

    def build(self, raw: Mapping[str, str]) -> Dict[str, Any]:
        converted: Dict[str, Any] = {
            fld: self.registry.convert(fld, raw_val)
            for fld, raw_val in raw.items()
        }
        record = GSODRecord.model_validate(converted)
        return record.model_dump()
