import tarfile
import io
import pytest
from etl.downloader.tar_extractor import TarExtractor

@pytest.fixture
def sample_tar(tmp_path):
    tar_path = tmp_path / "sample.tar"
    with tarfile.open(tar_path, "w") as tf:
        # good CSV
        info = tarfile.TarInfo("foo.csv")
        data = b"hello"
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
        # non-csv
        info2 = tarfile.TarInfo("bar.txt")
        info2.size = 3
        tf.addfile(info2, io.BytesIO(b"123"))
    return tar_path

def test_extract_only_csv(tmp_path, sample_tar):
    dest = tmp_path / "out"
    ex = TarExtractor()
    files = ex.extract(sample_tar, dest)
    assert len(files) == 1
    assert files[0].name == "foo.csv"
    assert (dest/"foo.csv").read_bytes() == b"hello"
