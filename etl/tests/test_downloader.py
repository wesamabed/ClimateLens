# etl/tests/test_downloader.py
import requests
from etl.downloader import download_year

class DummyResponse:
    def __init__(self, data: bytes, status=200):
        self._data = data
        self.status_code = status
        self.headers = {"content-length": str(len(data))}
    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"Status {self.status_code}")
    def iter_content(self, chunk_size=1):
        for i in range(0, len(self._data), chunk_size):
            yield self._data[i:i+chunk_size]

def test_download_and_skip(tmp_path, monkeypatch):
    year = 2020
    sample = b"id,date,temp\n1,2020-01-01,5.0\n"
    calls = {"count": 0}

    def fake_get(url, stream, timeout):
        calls["count"] += 1
        return DummyResponse(sample)

    monkeypatch.setattr(requests, "get", fake_get)
    out = download_year(year, tmp_path)
    assert out.exists()
    assert out.read_bytes() == sample

    # Second call should skip download
    out2 = download_year(year, tmp_path)
    assert calls["count"] == 1
    assert out2 == out
