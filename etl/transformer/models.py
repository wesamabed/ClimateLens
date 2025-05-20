# etl/transformer/models.py
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class GSODRecord(BaseModel):
    # identifiers & metadata
    station:    str          = Field(alias="STATION")
    record_date: date        = Field(alias="DATE")
    latitude:   Optional[float]        = Field(alias="LATITUDE")
    longitude:  Optional[float]        = Field(alias="LONGITUDE")
    elevation:  Optional[float] = Field(alias="ELEVATION")
    name:       Optional[str]   = Field(alias="NAME")

    # temperature & its quality flag
    temp:       Optional[float] = Field(alias="TEMP")
    temp_attr:  Optional[int]   = Field(alias="TEMP_ATTRIBUTES")

    dewp:       Optional[float] = Field(alias="DEWP")
    dewp_attr:  Optional[int]   = Field(alias="DEWP_ATTRIBUTES")

    # pressures & flags
    slp:        Optional[float] = Field(alias="SLP")
    slp_attr:   Optional[int]   = Field(alias="SLP_ATTRIBUTES")

    stp:        Optional[float] = Field(alias="STP")
    stp_attr:   Optional[int]   = Field(alias="STP_ATTRIBUTES")

    # visibility & flag
    visib:      Optional[float] = Field(alias="VISIB")
    visib_attr: Optional[int]   = Field(alias="VISIB_ATTRIBUTES")

    # wind speeds & flag
    wdsp:       Optional[float] = Field(alias="WDSP")
    wdsp_attr:  Optional[int]   = Field(alias="WDSP_ATTRIBUTES")

    mxspd:      Optional[float] = Field(alias="MXSPD")
    gust:       Optional[float] = Field(alias="GUST")

    # max/min temps & flags
    max_temp:   Optional[float] = Field(alias="MAX")
    max_attr:   Optional[int]   = Field(alias="MAX_ATTRIBUTES")

    min_temp:   Optional[float] = Field(alias="MIN")
    min_attr:   Optional[int]   = Field(alias="MIN_ATTRIBUTES")

    # precipitation & flag
    prcp:       Optional[float] = Field(alias="PRCP")
    prcp_attr:  Optional[str]   = Field(alias="PRCP_ATTRIBUTES")  # often a letter flag

    # snow depth (no separate “attributes” column in CSV)
    sndp:       Optional[float] = Field(alias="SNDP")

    # weather‐phenomena flags: F=Fog, R=Rain, S=Snow, H=Hail, T=Thunder, T=Tornado
    frshtt_fog:     bool
    frshtt_rain:    bool
    frshtt_snow:    bool
    frshtt_hail:    bool
    frshtt_thunder: bool
    frshtt_tornado: bool

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
