# etl/tests/test_cli_integration.py

import sys
from pathlib import Path
import pytest

from etl.main import main
from etl.loader.repository import MongoRepository
from etl.pipeline.download_step import DownloadStep
from etl.pipeline.transform_step import TransformStep
from etl.pipeline.load_step import LoadStep

def test_dry_run_creates_data(tmp_path, monkeypatch, capsys):
    # 1) Stub out MongoRepository.count_for_year so we never hit a real DB
    monkeypatch.setattr(MongoRepository, "count_for_year", lambda self, year: 0)

    # 2) Stub DownloadStep.execute to create raw/<year>/gsod_<year>.tar files
    def fake_download_execute(self, years):
        data_root = Path(self.config.DATA_DIR)
        for y in years:
            raw_dir = data_root / "raw" / str(y)
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / f"gsod_{y}.tar").touch()
        print("Starting DownloadStep")
        return []  # no actual .op files needed here
    monkeypatch.setattr(DownloadStep, "execute", fake_download_execute)

    # 3) Stub TransformStep.execute to just print its line
    monkeypatch.setattr(TransformStep, "execute",
                        lambda self, files: print("Starting TransformStep"))

    # 4) Fail if LoadStep.execute ever gets called
    monkeypatch.setattr(LoadStep, "execute",
                        lambda self, recs: pytest.fail("LoadStep should not be called in dry-run"))

    # 5) Patch sys.argv to simulate the CLI call
    monkeypatch.setattr(sys, "argv", [
        "etl.main",
        "--start-year", "2000",
        "--end-year",   "2000",
        "--dry-run",
        "--data-dir",   str(tmp_path / "data"),
        "--uri",        "mongodb://dry"
    ])

    # 6) Run the CLI entrypoint
    main()

    # 7) Capture stdout and assert on it
    out = capsys.readouterr().out
    assert "Starting DownloadStep" in out
    assert "Starting TransformStep" in out
    assert "LoadStep" not in out

    # 8) Check that the raw/2000 directory was created
    assert (tmp_path / "data" / "raw" / "2000").exists()
