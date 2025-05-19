# etl/tests/test_transformer_models.py
from datetime import date
import pytest
from pydantic import ValidationError
from etl.transformer.models import GSODRecord

# all of the aliases your GSODRecord currently defines—
# note that every Field(alias=...) must appear here
REQUIRED_FIELDS = {
    "STN---":        "010010",
    "WBAN":          "99999",
    "TEMP_value":    "32.0",
    "TEMP_obs":      "1",
    "DEWP_value":    "30.0",
    "DEWP_obs":      "2",
    "SLP_value":     "1015.0",
    "SLP_obs":       "3",
    "STP_value":     "1010.0",
    "STP_obs":       "4",
    "VISIB_value":   "10.0",
    "VISIB_obs":     "5",
    "WDSP_value":    "5.0",
    "WDSP_obs":      "6",
    "MXSPD":         "8.0",
    "GUST":          "12.0",
    "MAX":           "40.0",
    "MIN":           "20.0",
    "PRCP":          "0.10",
    "SNDP":          "1.0",
    # the six split flags instead of a single "FRSHTT"
    "FRSHTT_fog":     "0",
    "FRSHTT_rain":    "0",
    "FRSHTT_snow":    "0",
    "FRSHTT_hail":    "0",
    "FRSHTT_thunder": "0",
    "FRSHTT_tornado": "0",
}

def test_pydantic_model_full():
    raw = {
        **REQUIRED_FIELDS,
        "YEARMODA": "20210101",   # valid date
    }
    rec = GSODRecord.model_validate(raw)

    # basic identity checks
    assert rec.station_id == "010010"
    assert rec.wban == "99999"

    # date parsing
    assert isinstance(rec.record_date, date)
    assert rec.record_date == date(2021, 1, 1)

    # raw TEMP_value should be parsed as float, un-converted
    assert pytest.approx(rec.temp_mean_c, rel=1e-3) == 32.0
    assert rec.temp_obs == 1

    # spot-check another numeric field
    assert pytest.approx(rec.dewp_c, rel=1e-3) == 30.0

    # and one of the flag fields
    assert rec.frshtt_fog == 0
    assert rec.frshtt_tornado == 0

def test_invalid_date():
    raw = {
        **REQUIRED_FIELDS,
        "YEARMODA": "bad-date",  # invalid!
    }
    with pytest.raises(ValidationError):
        GSODRecord.model_validate(raw)
