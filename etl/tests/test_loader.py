import logging
from pathlib import Path

from etl.loader.loader import BatchLoader
from etl.config import ETLConfig  # assuming ETLConfig is defined here

def test_load_batches(tmp_path: Path):
    # Create 2,500 dummy records.
    records = [{"val": i} for i in range(2500)]
    # Set CHUNK_SIZE to 1,000 for batching.
    cfg = ETLConfig(
        MONGODB_URI="mongodb+srv://user:pw@host/test",
        DB_NAME="testdb",
        DATA_DIR=tmp_path,
        CHUNK_SIZE=1000,
        FTP_MAX_WORKERS=4,             # if required by ETLConfig
        FTP_RETRY_ATTEMPTS=3,          # if required by ETLConfig
        FTP_RETRY_WAIT=5               # if required by ETLConfig
    )

    # Create dummy preparer and repository.
    class DummyPreparer:
        def prepare(self, record):
            return record

    class DummyRepository:
        def __init__(self):
            self.inserted = []
        def bulk_insert(self, docs):
            self.inserted.extend(docs)

    dummy_repo = DummyRepository()
    logger = logging.getLogger("BatchLoaderTest")
    logger.setLevel(logging.INFO)
    loader = BatchLoader(
        preparer=DummyPreparer(),
        repository=dummy_repo,
        batch_size=cfg.CHUNK_SIZE,
        max_workers=1,
        logger=logger,
    )
    loader.load(records)
    assert len(dummy_repo.inserted) == len(records)