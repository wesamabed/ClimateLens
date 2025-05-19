# etl/tests/test_tar_extractor.py
import tarfile
import gzip
import io
from pathlib import Path

from etl.downloader.tar_extractor import TarExtractor

def make_test_tar(tmp_path: Path) -> Path:
    tar_path = tmp_path / "test.tar"
    with tarfile.open(tar_path, "w") as tf:
        # add one .op.gz member
        data = gzip.compress(b"HELLO")
        mi = tarfile.TarInfo("foo.op.gz")
        mi.size = len(data)
        tf.addfile(mi, io.BytesIO(data))
        # add one non‐.op.gz member
        mi2 = tarfile.TarInfo("ignore.txt")
        mi2.size = 0
        tf.addfile(mi2, None)
    return tar_path

def test_extract_op_gz(tmp_path):
    tar = make_test_tar(tmp_path)
    extractor = TarExtractor()
    dest = tmp_path / "out"
    files = extractor.extract_op_gz(tar, dest)
    assert len(files) == 1
    out_file = files[0]
    assert out_file.name == "foo.op.gz"
    # content round‐trips
    with gzip.open(out_file, "rb") as f:
        assert f.read() == b"HELLO"
