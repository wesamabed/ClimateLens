import io
from etl.transformer.parser import CsvParser

CSV = """A,B,FRSHTT
1,2,101010
3,4,??????
"""

def test_csv_parser_flags(monkeypatch):
    parser = CsvParser()
    f = io.StringIO(CSV)
    rows = list(parser.parse(f))
    assert rows[0]["A"] == "1"
    # first row flags → [1,0,1,0,1,0]
    assert rows[0]["frshtt_fog"]
    assert not rows[0]["frshtt_rain"]
    # second row: bad raw → all False
    assert not any(rows[1][k] for k in rows[1] if k.startswith("frshtt_"))
