import pytest
from pathlib import Path
from etl.downloader.http_downloader import HTTPDownloader

class FakeResponse:
    def __init__(self, status=200, chunks=None):
        self.status = status
        self._chunks = chunks or [b"abc", b"def"]
    def raise_for_status(self):
        if not (200 <= self.status < 300):
            raise IOError("bad status")
    def iter_content(self, chunk_size):
        yield from self._chunks

@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path / "out"

def test_download_year_tar_success(tmp_dir, monkeypatch):
    calls = []
    def fake_get(url, stream, timeout):
        calls.append(url)
        return FakeResponse()
    monkeypatch.setattr("requests.get", fake_get)

    dl = HTTPDownloader(base_url="http://base", retry_attempts=2, retry_wait=0)
    out = dl.download_year_tar(2021, tmp_dir)
    assert out.exists()
    assert tmp_dir.joinpath("2021","2021.tar.gz").exists()
    assert calls == ["http://base/2021.tar.gz"]

def test_download_years_parallel(tmp_dir, monkeypatch):
    created = []

    # signature now takes self, year, dest_dir
    def fake_year_tar(self, year, dest):
        p = dest/str(year)/f"{year}.tar.gz"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"")
        created.append(year)
        return p

    monkeypatch.setattr(HTTPDownloader, "download_year_tar", fake_year_tar)
    dl = HTTPDownloader()
    results = dl.download_years([2019, 2020], tmp_dir, max_workers=2)

    assert set(created) == {2019, 2020}
    assert all(isinstance(p, Path) for p in results)
    assert len(results) == 2

