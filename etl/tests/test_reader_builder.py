import logging
import pytest
from etl.transformer.reader import CsvReader
from etl.transformer.builder import PydanticRecordBuilder
from etl.transformer.parser import CsvParser

SAMPLE = '''"STATION","DATE","LATITUDE","LONGITUDE","ELEVATION","NAME",\
"TEMP","TEMP_ATTRIBUTES","DEWP","DEWP_ATTRIBUTES","SLP","SLP_ATTRIBUTES",\
"STP","STP_ATTRIBUTES","VISIB","VISIB_ATTRIBUTES","WDSP","WDSP_ATTRIBUTES",\
"MXSPD","GUST","MAX","MAX_ATTRIBUTES","MIN","MIN_ATTRIBUTES",\
"PRCP","PRCP_ATTRIBUTES","SNDP","FRSHTT"
"01001","2020-01-01","10.0","20.0","5.0","X","32","24","30","24","1000","24",\
"999.9","0","10","6","5","24","10","15","50","12","*","","0.1","G","0.0","101000"
'''

def test_reader_and_builder(tmp_path, caplog):
    # write temp file
    path = tmp_path / "t.csv"
    path.write_text(SAMPLE)
    parser = CsvParser()
    logger = logging.getLogger("test_reader_builder")
    logger.setLevel(logging.DEBUG)
    builder = PydanticRecordBuilder(logger)
    reader = CsvReader(parser, builder, logger)
    recs = reader.read(path)
    assert len(recs) == 1
    r = recs[0]
    # check some fields
    assert r["station"] == "01001"
    assert r["temp"] == pytest.approx(0.0)
    assert r["frshtt_fog"] is True
