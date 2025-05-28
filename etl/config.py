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
    DATA_DIR_IPCC: Path = Field(default=Path("data/ipcc"))
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
    IPCC_PDF_URL: str = Field(
        default="https://ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf",
        description="Download URL for the AR6 WG-I Summary-for-Policymakers PDF",
    )
    IPCC_PDF_NAME: str = Field(default="IPCC_AR6_WGI_SPM.pdf")
    IPCC_CHUNK_WORDS: int = Field(default=250, ge=50, le=500)
    EMBED_BATCH_SIZE: PositiveInt = Field(default=1, ge=1)
    VERTEX_PROJECT: Optional[str] = None
    VERTEX_REGION: Optional[str] = "us-central1"
    VERTEX_MODEL: str = "gemini-embedding-001"
    # ... plus Atlas admin creds if you’ll automate index:
    ATLAS_PROJECT_ID: Optional[str] = None
    ATLAS_CLUSTER: Optional[str] = None
    ATLAS_PUBLIC_KEY: Optional[str] = None
    ATLAS_PRIVATE_KEY: Optional[str] = None
    REINDEX: bool = Field(
        default=False,
        description="If true, reindex the MongoDB collection. "
                    "Use with caution, as it will drop existing indexes."
    )
    

    # skip flags (only via CLI, not env)
    SKIP_GSOD: bool = Field(default=False, description="If true, do not run the GSOD pipeline")
    SKIP_CO2:  bool = Field(default=False, description="If true, do not run the CO₂ pipeline")
    SKIP_IPCC: bool = Field(default=False, description="If true, do not run the IPCC pipeline")
    SKIP_EMBED: bool = Field(
        default=False,
        description="If true, skip the embedding step. "
                    "Useful for debugging or if you want to run the pipeline without embeddings."
    )


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
    data_dir_ipcc: Optional[str] = None,
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
    skip_ipcc: Optional[bool] = None,
    skip_embed: Optional[bool] = None,
    ipcc_pdf_url: Optional[str] = None,
    ipcc_pdf_name: Optional[str] = None,
    ipcc_chunk_words: Optional[int] = None,
    embed_batch_size: Optional[int] = None,
    vertex_project: Optional[str] = None,
    vertex_region: Optional[str] = None,
    vertex_model: Optional[str] = None,
    atlas_project_id: Optional[str] = None,
    atlas_cluster: Optional[str] = None,
    atlas_public_key: Optional[str] = None,
    atlas_private_key: Optional[str] = None,
    reindex: Optional[bool] = None

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
    if data_dir_ipcc is not None:
        overrides["DATA_DIR_IPCC"] = Path(data_dir_ipcc)
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
    if skip_ipcc is not None:
        overrides["SKIP_IPCC"] = skip_ipcc
    if skip_embed is not None:
        overrides["SKIP_EMBED"] = skip_embed
    if ipcc_pdf_url is not None:
        overrides["IPCC_PDF_URL"] = ipcc_pdf_url
    if ipcc_pdf_name is not None:
        overrides["IPCC_PDF_NAME"] = ipcc_pdf_name
    if ipcc_chunk_words is not None:    
        overrides["IPCC_CHUNK_WORDS"] = ipcc_chunk_words
    if embed_batch_size is not None:
        overrides["EMBED_BATCH_SIZE"] = embed_batch_size        
    if vertex_project is not None:
        overrides["VERTEX_PROJECT"] = vertex_project
    if vertex_region is not None:
        overrides["VERTEX_REGION"] = vertex_region
    if vertex_model is not None:
        overrides["VERTEX_MODEL"] = vertex_model
    if atlas_project_id is not None:
        overrides["ATLAS_PROJECT_ID"] = atlas_project_id
    if atlas_cluster is not None:
        overrides["ATLAS_CLUSTER"] = atlas_cluster
    if atlas_public_key is not None:    
        overrides["ATLAS_PUBLIC_KEY"] = atlas_public_key
    if atlas_private_key is not None:
        overrides["ATLAS_PRIVATE_KEY"] = atlas_private_key
    if reindex is not None:
        overrides["REINDEX"] = reindex 

    env_path = os.environ.get("ETL_ENV_PATH")
    if env_path:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)

    try:
        return ETLConfig(**overrides)
    except Exception as e:
        raise ValueError(e)