from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator

def _strip_flag(v: str) -> str:
    # Remove any non-digit/dot (so flags like “G” get dropped)
    return "".join(ch for ch in v if ch.isdigit() or ch in ".-")

class GSODRecord(BaseModel):
    station_id: str    = Field(alias="STN---")
    wban:       str    = Field(alias="WBAN")
    record_date: date  = Field(alias="YEARMODA")

    temp_mean_c: Optional[float]  = Field(alias="TEMP_value")
    temp_obs:    Optional[int]    = Field(alias="TEMP_obs")
    dewp_c:      Optional[float]  = Field(alias="DEWP_value")
    dewp_obs:    Optional[int]    = Field(alias="DEWP_obs")

    slp_mbar:    Optional[float]  = Field(alias="SLP_value")
    slp_obs:     Optional[int]    = Field(alias="SLP_obs")
    stp_mbar:    Optional[float]  = Field(alias="STP_value")
    stp_obs:     Optional[int]    = Field(alias="STP_obs")

    visib_km:    Optional[float]  = Field(alias="VISIB_value")
    visib_obs:   Optional[int]    = Field(alias="VISIB_obs")

    wdsp_ms:     Optional[float]  = Field(alias="WDSP_value")
    wdsp_obs:    Optional[int]    = Field(alias="WDSP_obs")

    mxspd_ms:    Optional[float]  = Field(alias="MXSPD")
    gust_ms:     Optional[float]  = Field(alias="GUST")

    max_temp_c:  Optional[float]  = Field(alias="MAX")
    min_temp_c:  Optional[float]  = Field(alias="MIN")

    prcp_mm:     Optional[float]  = Field(alias="PRCP")
    sndp_mm:     Optional[float]  = Field(alias="SNDP")

    frshtt_fog:     Optional[int] = Field(alias="FRSHTT_fog")
    frshtt_rain:    Optional[int] = Field(alias="FRSHTT_rain")
    frshtt_snow:    Optional[int] = Field(alias="FRSHTT_snow")
    frshtt_hail:    Optional[int] = Field(alias="FRSHTT_hail")
    frshtt_thunder: Optional[int] = Field(alias="FRSHTT_thunder")
    frshtt_tornado: Optional[int] = Field(alias="FRSHTT_tornado")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

    @field_validator("record_date", mode="before")
    def parse_date(cls, v):
        return datetime.strptime(str(v), "%Y%m%d").date()
