# etl/tests/test_converter.py
import pytest
from etl.transformer.converter import (
    FahrenheitToCelsiusConverter, PressureConverter,
    VisibilityConverter, WindConverter,
    PrecipSnowConverter, ConverterRegistry
)

def test_fahrenheit_to_celsius():
    c = FahrenheitToCelsiusConverter()
    assert pytest.approx(c.convert("32")) == 0
    assert c.convert("999.9") is None

def test_pressure():
    p = PressureConverter()
    assert pytest.approx(p.convert("1016.6")) == 1016.6
    assert p.convert("9999.9") is None

def test_visibility():
    v = VisibilityConverter()
    assert pytest.approx(v.convert("1")) == pytest.approx(1 * 1.60934)
    assert v.convert("999.9") is None

def test_wind():
    w = WindConverter()
    assert pytest.approx(w.convert("10")) == pytest.approx(10 * 0.514444)
    assert w.convert("999.9") is None

def test_precip_snow():
    ps = PrecipSnowConverter()
    assert pytest.approx(ps.convert("1")) == pytest.approx(25.4)
    assert ps.convert("99.99") is None

def test_registry_fallback():
    reg = ConverterRegistry([FahrenheitToCelsiusConverter()])
    # unknown field => raw returned
    assert reg.convert("NOT_A_FIELD", "123") == "123"
