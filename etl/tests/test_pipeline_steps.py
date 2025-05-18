# etl/tests/test_pipeline_steps.py
import logging
import pytest
from pathlib import Path
from etl.pipeline.download_step import DownloadStep
from etl.pipeline.transform_step import TransformStep
from etl.pipeline.load_step import LoadStep
from etl.config import ETLConfig

class DummyDownloader:
    def download_years(self, years, dest_dir, max_workers):
        # create one dummy file per year
        paths = []
        for y in years:
            p = dest_dir / f"dummy_{y}.op.gz"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("dummy")
            paths.append(p)
        return paths

class DummyExtractor:
    def extract_op_gz(self, tar, dest):
        return [tar]  # pass through

class DummyTransformer:
    def transform(self, paths):
        return [{"file": p.name} for p in paths]

class DummyLoader:
    def __init__(self):
        self.loaded = []
    def load(self, recs):
        self.loaded.extend(recs)

@pytest.fixture
def cfg(tmp_path):
    return ETLConfig(
        MONGODB_URI="mongodb://xx", DB_NAME="db",
        DATA_DIR=tmp_path, CHUNK_SIZE=10
    )

@pytest.fixture
def logger():
    return logging.getLogger("test")

def test_download_and_transform_and_load(cfg, logger, tmp_path):
    dl_step = DownloadStep(cfg, DummyDownloader(), DummyExtractor(), logger)
    files = dl_step.execute()
    assert all(f.exists() for f in files)

    tr_step = TransformStep(cfg, DummyTransformer(), logger)
    recs = tr_step.execute(files)
    assert recs and recs[0]["file"].endswith(".op.gz")

    dummy_loader = DummyLoader()
    ld_step = LoadStep(cfg, dummy_loader, logger)
    ld_step.execute(recs)
    assert dummy_loader.loaded == recs
