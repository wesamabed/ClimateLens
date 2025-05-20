import logging
from etl.loader.loader import BatchLoader

class DummyRepo:
    def __init__(self): self.inserted = []
    def bulk_insert(self, docs): self.inserted.append(list(docs))

class DummyPrep:
    def prepare(self, r): return {"id": r["x"]}

def test_batchloader_splits_and_inserts(tmp_path):
    repo = DummyRepo()
    prep = DummyPrep()
    logger = logging.getLogger("test_loader")
    logger.setLevel(logging.DEBUG)
    loader = BatchLoader(prep, repo, batch_size=2, max_workers=2, logger=logger, retry_attempts=1)
    records = [{"x":1},{"x":2},{"x":3}]
    loader.load(records)
    # 2 batches: [1,2], [3]
    assert len(repo.inserted) == 2
    assert [{"id":1},{"id":2}] in repo.inserted
    assert [{"id":3}] in repo.inserted
