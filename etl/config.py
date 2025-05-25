from pathlib import Path
import os
from datetime import datetime
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PositiveInt, field_validator
from typing import Optional, Dict

# ─── single source‐of‐truth .env loader ─────────────────────────────
ENV_PATH = Path(__file__).parent.parent / "server" / ".env"
if not ENV_PATH.exists():
    raise FileNotFoundError(f"Missing config file: {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH, override=False)

class ETLConfig(BaseSettings):
    """
    • SRP: only handles configuration
    • DIP: consumers depend on this abstraction, not on os.environ
    • Factory Pattern: BaseSettings as config factory
    """
    model_config = SettingsConfigDict(
        env_file=None,      # already loaded by python‐dotenv
        extra="ignore",     # ignore unrelated vars
    )

    # MongoDB
    MONGODB_URI: str         = Field(..., min_length=12)
    DB_NAME:     str         = Field(..., min_length=1)

    # local storage
    DATA_DIR:    Path        = Field(default=Path("data/gsod"))
    CHUNK_SIZE:  PositiveInt = Field(default=5000, ge=1)

    # year range flags
    START_YEAR:  int         = Field(
        default=1929,
        ge=1900,
        le=datetime.utcnow().year,
        description="Earliest GSOD year to fetch"
    )
    END_YEAR:    int         = Field(
        default_factory=lambda: datetime.utcnow().year,
        ge=1929,
        description="Latest GSOD year to fetch"
    )

    # HTTP downloader settings
    DOWNLOAD_BASE_URL:   str         = Field(default="https://www.ncei.noaa.gov/data/global-summary-of-the-day/archive")
    DOWNLOAD_RETRY_ATTEMPTS:  PositiveInt = Field(default=3, ge=1)
    DOWNLOAD_RETRY_WAIT:      PositiveInt = Field(default=5, ge=0)
    DOWNLOAD_MAX_WORKERS:     PositiveInt = Field(default=4, ge=1)

    # LOADER SETTINGS
    LOAD_MAX_WORKERS: PositiveInt = Field(default=4, ge=1, description="Max threads for DB load")

    # CO₂-pipeline settings
    CO2_INDICATOR:    str = Field(
        default="EN.GHG.CO2.MT.CE.AR5",
        description="World Bank indicator code for CO₂ emissions"
    )
    CO2_START_YEAR:   int = Field(
        default=1960,
        ge=1900,
        le=datetime.utcnow().year,
        description="Earliest CO₂ year to fetch"
    )
    CO2_END_YEAR:     int = Field(
        default_factory=lambda: datetime.utcnow().year,
        ge=1960,
        le=datetime.utcnow().year,
        description="Latest CO₂ year to fetch"
    )

    # skip flags (only via CLI, not env)
    SKIP_GSOD: bool = Field(default=False, description="If true, do not run the GSOD pipeline")
    SKIP_CO2:  bool = Field(default=False, description="If true, do not run the CO₂ pipeline")


    @field_validator("MONGODB_URI")
    def validate_uri(cls, v):
        if not (v.startswith("mongodb://") or v.startswith("mongodb+srv://")):
            raise ValueError("Invalid MONGODB_URI")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # sanity checks
        if not self.MONGODB_URI.startswith("mongodb"):
            raise ValueError("MONGODB_URI doesn’t look like a valid Mongo URI")
        # ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_config(
    uri: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db_name: Optional[str] = None,
    data_dir: Optional[str] = None,
    chunk_size: Optional[int] = None,
    download_base_url: Optional[str]       = None,
    download_retry_attempts: Optional[int] = None,
    download_retry_wait: Optional[int] = None,
    download_max_workers: Optional[int] = None,
    load_max_workers: Optional[int] = None,
    co2_indicator: Optional[str] = None,
    co2_start_year: Optional[int] = None,
    co2_end_year: Optional[int] = None,
    skip_gsod: Optional[bool] = None,
    skip_co2: Optional[bool]  = None,

) -> ETLConfig:
    """
    Build and return an ETLConfig, applying any CLI overrides.
    """
    overrides: Dict[str, object] = {}
    if uri is not None:
        overrides["MONGODB_URI"] = uri
    if db_name is not None:
        overrides["DB_NAME"] = db_name
    if start_year is not None:
        overrides["START_YEAR"] = start_year
    if end_year is not None:
        overrides["END_YEAR"] = end_year
    if data_dir is not None:
        overrides["DATA_DIR"] = Path(data_dir)
    if chunk_size is not None:
        overrides["CHUNK_SIZE"] = chunk_size
    if download_base_url is not None:
        overrides["DOWNLOAD_BASE_URL"] = download_base_url
    if download_retry_attempts is not None:
        overrides["DOWNLOAD_RETRY_ATTEMPTS"] = download_retry_attempts
    if download_retry_wait is not None:
        overrides["DOWNLOAD_RETRY_WAIT"] = download_retry_wait
    if download_max_workers is not None:
        overrides["DOWNLOAD_MAX_WORKERS"] = download_max_workers
    if load_max_workers is not None:
        overrides["LOAD_MAX_WORKERS"] = load_max_workers
    if co2_indicator is not None:
        overrides["CO2_INDICATOR"] = co2_indicator
    if co2_start_year is not None:
        overrides["CO2_START_YEAR"] = co2_start_year
    if co2_end_year is not None:
        overrides["CO2_END_YEAR"] = co2_end_year
    if skip_gsod is not None:
        overrides["SKIP_GSOD"] = skip_gsod
    if skip_co2 is not None:
        overrides["SKIP_CO2"] = skip_co2

    env_path = os.environ.get("ETL_ENV_PATH")
    if env_path:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)

    try:
        return ETLConfig(**overrides)
    except Exception as e:
        raise ValueError(e)