import os
from pathlib import Path
import pytest
from etl.config import get_config, ETLConfig

ENV_BACKUP = dict(os.environ)

@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    # Override DB_NAME to ensure it's "testdb"
    monkeypatch.setenv("DB_NAME", "testdb")
    fake_env = tmp_path / ".env"
    fake_env.write_text("MONGODB_URI=mongodb://x:1\nDB_NAME=testdb\n")
    monkeypatch.setenv("ETL_ENV_PATH", str(fake_env))
    yield
    os.environ.update(ENV_BACKUP)

def test_default_config():
    cfg = get_config()
    assert isinstance(cfg, ETLConfig)
    assert cfg.MONGODB_URI.startswith(("mongodb://", "mongodb+srv://"))  # Allow both prefixes
    assert cfg.DB_NAME == "testdb"
    # defaults
    assert cfg.START_YEAR <= cfg.END_YEAR

def test_override_cli(monkeypatch):
    cfg = get_config(uri="mongodb://foo", start_year=2000, end_year=2005)
    assert cfg.MONGODB_URI == "mongodb://foo"
    assert cfg.START_YEAR == 2000
    assert cfg.END_YEAR == 2005

def test_invalid_uri(monkeypatch):
    # if .env has bad URI
    bad_env = Path(os.environ["ETL_ENV_PATH"])
    bad_env.write_text("MONGODB_URI=foo\nDB_NAME=x\n")
    with pytest.raises(ValueError):
        _ = get_config()