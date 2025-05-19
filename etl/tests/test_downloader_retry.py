# etl/tests/test_downloader_retry.py
import ftplib
import pytest
from etl.downloader.ftp_downloader import FTPDownloader

class FailingFTP:
    def __init__(self, host, timeout): pass
    def login(self, u, p): pass
    def cwd(self, p): pass
    def retrbinary(self, cmd, cb):
        raise ftplib.error_temp("Temporary failure")
    def __enter__(self): return self
    def __exit__(self,*a): return False

def test_retry_exhaust(monkeypatch, tmp_path):
    monkeypatch.setattr(ftplib, "FTP", FailingFTP)
    ftp = FTPDownloader(host="h", user="u", passwd="p", retry_attempts=2, retry_wait=0)
    with pytest.raises(ftplib.error_temp):
        ftp.download_year_tar(2020, tmp_path)
