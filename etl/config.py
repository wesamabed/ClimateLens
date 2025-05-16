from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PositiveInt

# ① Explicitly load the single source-of-truth .env
ENV_PATH = Path(__file__).parent.parent / "server" / ".env"
if not ENV_PATH.exists():
    raise FileNotFoundError(f"Missing config file: {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH, override=False)

class ETLConfig(BaseSettings):
    """
      Settings factory (Factory + DIP):
      - Reads os.environ after dotenv.
      - Validates types & defaults.
      - SRP: only manages configuration.
    """
    model_config = SettingsConfigDict(
        env_file=None,     # already loaded
        extra="ignore",    # ignore unexpected vars
    )

    MONGODB_URI: str         = Field(..., min_length=12)
    DATA_DIR:    Path        = Field(default=Path("data/gsod"))
    CHUNK_SIZE:  PositiveInt = Field(default=1000, ge=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Quick sanity check (Reliability)
        if not self.MONGODB_URI.startswith("mongodb"):
            raise ValueError("MONGODB_URI doesn’t look like a Mongo URI")

    @property
    def batch_size(self) -> int:
        """Alias for CHUNK_SIZE (OCP)."""
        return self.CHUNK_SIZE
