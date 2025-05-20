import logging
import mongomock
import pytest
from datetime import datetime
from etl.loader.repository import MongoRepository

@pytest.fixture(autouse=True)
def patch_mongo(monkeypatch):
    client = mongomock.MongoClient()
    monkeypatch.setattr("etl.loader.repository.MongoClient", lambda uri: client)
    return client

def test_count_and_insert(tmp_path):
    logger = logging.getLogger("test_repository")
    logger.setLevel(logging.DEBUG)
    cfg = type("DummyCfg", (), {
        "MONGODB_URI": "mongodb://localhost:27017", 
        "DB_NAME": "testdb"
    })()
    repo = MongoRepository(cfg=cfg, logger=logger)
    # seed some docs
    repo._col.insert_many([
        {"record_date": datetime(2020,1,5)},
        {"record_date": datetime(2021,1,5)}
    ])
    assert repo.count_for_year(2020) == 1
    # test bulk_insert with duplicates
    docs = [{"_id":1},{"_id":1},{"_id":2}]
    repo.bulk_insert(docs)
    # duplicate key should be skipped but non-duplicates inserted
    assert repo._col.count_documents({}) == 4  # 2 seeded + ids 1 and 2
