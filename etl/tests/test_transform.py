# etl/tests/test_transform.py
import pytest
from etl.pipeline.steps import TransformStep
from etl.config import ETLConfig

SAMPLE_CSV = """\
STN---,DATE,TEMP,MAX,MIN,PRCP
012345,20250101,10.0,15.0,5.0,0.0
678901,2025-02-28,12.5,18.2,6.1,1.2
badrow,notadate,abc,def,ghi,jkl
"""

@pytest.fixture
def sample_data_dir(tmp_path):
    csv_path = tmp_path / "gsod_sample.csv"
    csv_path.write_text(SAMPLE_CSV)
    return tmp_path

def test_transform_happy_and_bad_rows(sample_data_dir, caplog):
    cfg = ETLConfig(
        MONGODB_URI="mongodb://dummy",
        DATA_DIR=sample_data_dir
    )
    step = TransformStep(cfg)

    caplog.set_level("WARNING")
    records = step.execute()

    # Two valid records, one skipped
    assert len(records) == 2
    assert records[0]["stationId"] == "012345"
    assert records[1]["stationId"] == "678901"
    assert "Skipped bad row 3" in caplog.text

def test_transform_empty_dir(tmp_path):
    cfg = ETLConfig(
        MONGODB_URI="mongodb://dummy",
        DATA_DIR=tmp_path
    )
    step = TransformStep(cfg)
    records = step.execute()
    assert records == []
