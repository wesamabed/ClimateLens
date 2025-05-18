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

    # FTP downloader settings
    FTP_HOST:            str         = Field(default="ftp.ncei.noaa.gov")
    FTP_USER:            str         = Field(default="anonymous")
    FTP_PASS:            str         = Field(default="")
    FTP_RETRY_ATTEMPTS:  PositiveInt = Field(default=3, ge=1)
    FTP_RETRY_WAIT:      PositiveInt = Field(default=5, ge=0)
    FTP_MAX_WORKERS:     PositiveInt = Field(default=4, ge=1)

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
    ftp_retry_attempts: Optional[int] = None,
    ftp_retry_wait: Optional[int] = None,
    ftp_max_workers: Optional[int] = None,
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
    if ftp_retry_attempts is not None:
        overrides["FTP_RETRY_ATTEMPTS"] = ftp_retry_attempts
    if ftp_retry_wait is not None:
        overrides["FTP_RETRY_WAIT"] = ftp_retry_wait
    if ftp_max_workers is not None:
        overrides["FTP_MAX_WORKERS"] = ftp_max_workers

    env_path = os.environ.get("ETL_ENV_PATH")
    if env_path:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)

    try:
        return ETLConfig(**overrides)
    except Exception as e:
        raise ValueError(e)