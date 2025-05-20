from abc import ABC, abstractmethod
from typing import Any, Optional, List
from .utils import strip_flag

class Converter(ABC):
    @abstractmethod
    def supports(self, field: str) -> bool: ...
    @abstractmethod
    def convert(self, raw: Any) -> Any: ...

class FloatConverter(Converter):
    FIELDS = {"LATITUDE", "LONGITUDE", "ELEVATION"}
    def supports(self, f: str) -> bool: return f in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw).strip()
        return None if not s or s.lower()=="null" else float(s)

class AttributesConverter(Converter):
    def supports(self, f: str) -> bool:
        return f.endswith("_ATTRIBUTES") and f != "PRCP_ATTRIBUTES"
    def convert(self, raw: Any) -> Optional[int]:
        s = str(raw).strip()
        return int(s) if s.isdigit() else None

class FahrenheitToCelsiusConverter(Converter):
    FIELDS = {"TEMP","DEWP","MAX","MIN"}
    def supports(self, f: str) -> bool: return f in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if s in ("","999.9","9999.9"):
            return None
        try:
            f = float(strip_flag(s))
        except ValueError:
            return None
        return (f - 32) * 5.0 / 9.0

class PressureConverter(Converter):
    FIELDS = {"SLP","STP"}
    def supports(self, f: str) -> bool: return f in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw)
        if not s or s in ("9999.9",):
            return None
        try:
            return float(strip_flag(s))
        except ValueError:
            return None

class VisibilityConverter(Converter):
    FIELDS = {"VISIB"}
    def supports(self, f: str) -> bool: return f in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw).strip()
        if not s or s in ("999.9",):
            return None
        try:
            miles = float(strip_flag(s))
        except ValueError:
            return None
        return miles * 1.60934

class WindConverter(Converter):
    FIELDS = {"WDSP","MXSPD","GUST"}
    def supports(self, f: str) -> bool: return f in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw).strip()
        if not s or s in ("999.9",):
            return None
        try:
            kt = float(strip_flag(s))
        except ValueError:
            return None
        return kt * 0.514444

class PrecipSnowConverter(Converter):
    FIELDS = {"PRCP","SNDP"}
    def supports(self, f: str) -> bool: return f in self.FIELDS
    def convert(self, raw: Any) -> Optional[float]:
        s = str(raw).strip()
        if not s or s in ("99.99","999.9"):
            return None
        try:
            inches = float(strip_flag(s))
        except ValueError:
            return None
        return inches * 25.4

class ConverterRegistry:
    def __init__(self, converters: List[Converter]) -> None:
        self._converters = converters
    def convert(self, field: str, raw: Any) -> Any:
        for conv in self._converters:
            if conv.supports(field):
                return conv.convert(raw)
        return raw
