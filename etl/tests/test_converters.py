import pytest
from etl.transformer.converter import (
    FloatConverter, AttributesConverter,
    FahrenheitToCelsiusConverter
)

def test_float_converter_empty():
    conv = FloatConverter()
    assert conv.convert("") is None
    assert conv.convert("  ") is None

def test_float_converter_valid():
    conv = FloatConverter()
    assert conv.convert("3.14") == 3.14

def test_attributes_converter():
    conv = AttributesConverter()
    assert conv.convert("24") == 24
    assert conv.convert("*") is None

def test_fahrenheit_to_celsius():
    conv = FahrenheitToCelsiusConverter()
    # 32°F → 0°C
    assert pytest.approx(conv.convert("32"), rel=1e-3) == 0.0
    # sentinel
    assert conv.convert("999.9") is None
