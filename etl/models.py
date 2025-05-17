# etl/models.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class GSODRecord(BaseModel):
    """
    Pydantic schema for one GSOD line.
    - Aliases map raw CSV headers to attributes.
    - Validators handle date parsing.
    """
    stationId: str           = Field(..., alias="STN---")
    date:      datetime      = Field(..., alias="DATE")
    tempMeanC: Optional[float] = Field(None, alias="TEMP")
    tempMaxC:  Optional[float] = Field(None, alias="MAX")
    tempMinC:  Optional[float] = Field(None, alias="MIN")
    precipMm:  Optional[float] = Field(None, alias="PRCP")

    @validator("date", pre=True)
    def parse_date(cls, v):
        for fmt in ("%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(v.strip(), fmt)
            except Exception:
                continue
        raise ValueError(f"Invalid DATE format: {v}")
