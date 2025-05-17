# etl/config.py
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PositiveInt

# ─── Load single source-of-truth .env ──────────────────────────────────────────────
ENV_PATH = Path(__file__).parent.parent / "server" / ".env"
if not ENV_PATH.exists():
    raise FileNotFoundError(f"Missing config file: {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH, override=False)

class ETLConfig(BaseSettings):
    """
      Production-grade settings loader:
      • Factory Pattern: BaseSettings loads/validates os.environ.
      • SRP: only handles configuration.
      • DIP: callers depend on this abstraction.
    """
    model_config = SettingsConfigDict(
        env_file=None,    # already loaded via dotenv
        extra="ignore",   # ignore unrelated env vars
    )

    MONGODB_URI: str         = Field(..., min_length=12)
    DATA_DIR:    Path        = Field(default=Path("data/gsod"))
    CHUNK_SIZE:  PositiveInt = Field(default=1000, ge=1)
    START_YEAR:  int         = Field(default=1980, ge=1900)
    END_YEAR:    int         = Field(default_factory=lambda: datetime.now().year, ge=1900)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Quick sanity check
        if not self.MONGODB_URI.startswith("mongodb"):
            raise ValueError("MONGODB_URI doesn’t look like a Mongo URI")

    @property
    def batch_size(self) -> int:
        """Open/Closed: alias for CHUNK_SIZE."""
        return self.CHUNK_SIZE
