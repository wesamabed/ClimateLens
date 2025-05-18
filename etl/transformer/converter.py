from abc import ABC, abstractmethod
from typing import Any, Optional, List
from .models import _strip_flag

class Converter(ABC):
    @abstractmethod
    def supports(self, field: str) -> bool: ...
    @abstractmethod
    def convert(self, raw: Any) -> Any: ...

class FahrenheitToCelsiusConverter(Converter):
    # Convert temperature fields.
    FIELDS = {"TEMP_value", "DEWP_value", "MAX", "MIN"}
    def supports(self, field: str) -> bool:
        return field in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if s in ("", "999.9", "9999.9"):
            return None
        f = float(_strip_flag(s))
        return (f - 32) * 5.0 / 9.0

class PressureConverter(Converter):
    FIELDS = {"SLP_value", "STP_value"}
    def supports(self, field: str) -> bool:
        return field in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if s in ("", "9999.9"):
            return None
        return float(_strip_flag(s))

class VisibilityConverter(Converter):
    FIELDS = {"VISIB_value"}
    def supports(self, field: str) -> bool:
        return field in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if s in ("", "999.9"):
            return None
        miles = float(_strip_flag(s))
        return miles * 1.60934

class WindConverter(Converter):
    FIELDS = {"WDSP_value", "MXSPD", "GUST"}
    def supports(self, field: str) -> bool:
        return field in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if s in ("", "999.9"):
            return None
        kt = float(_strip_flag(s))
        return kt * 0.514444

class PrecipSnowConverter(Converter):
    FIELDS = {"PRCP", "SNDP"}
    def supports(self, field: str) -> bool:
        return field in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if s in ("", "99.99", "999.9"):
            return None
        inches = float(_strip_flag(s))
        return inches * 25.4

class ConverterRegistry:
    def __init__(self, converters: List[Converter]) -> None:
        self._converters = converters
    def convert(self, field: str, raw: Any) -> Any:
        for conv in self._converters:
            if conv.supports(field):
                return conv.convert(raw)
        return raw