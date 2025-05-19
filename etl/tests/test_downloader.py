# etl/tests/test_downloader.py
from __future__ import annotations

import pytest
import ftplib
import logging
import tarfile
import io

from etl.downloader.ftp_downloader import FTPDownloader
from etl.downloader.tar_extractor import TarExtractor

class DummyFTP:
    def __init__(self, host, timeout):
        pass
    def login(self, user, passwd):
        pass
    def cwd(self, path):
        pass
    def retrbinary(self, cmd, cb):
        # build an in‐memory .tar with one dummy.op.gz file
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as t:
            ti = tarfile.TarInfo("foo.op.gz")
            data = b"hello"
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
        buf.seek(0)
        cb(buf.read())

    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False

@pytest.fixture(autouse=True)
def patch_ftp(monkeypatch):
    monkeypatch.setattr(ftplib, "FTP", DummyFTP)

def test_ftp_and_extract(tmp_path):
    logger = logging.getLogger("test")
    cfg_data_dir = tmp_path / "gsod"
    ftp = FTPDownloader(
        host="irrelevant",
        user="u", passwd="p",
        retry_attempts=1, retry_wait=0,
        logger=logger,
    )
    # download year 2022
    tar_paths = ftp.download_years([2022], cfg_data_dir, max_workers=1)
    assert len(tar_paths) == 1
    tar_path = tar_paths[0]
    assert tar_path.exists() and tar_path.name == "gsod_2022.tar"

    # extract it
    extractor = TarExtractor(logger=logger)
    out = extractor.extract_op_gz(tar_path, cfg_data_dir / "2022")
    assert len(out) == 1
    assert out[0].read_bytes() == b"hello"
