import logging
import io
import tarfile
from etl.pipeline.pipeline import Pipeline
from etl.pipeline.download_step import DownloadStep
from etl.pipeline.transform_step import TransformStep
from etl.pipeline.load_step import LoadStep

from etl.downloader.protocols import Downloader, ArchiveExtractor
from etl.transformer.concurrent import ConcurrentTransformer
from etl.loader.loader import BatchLoader
from etl.loader.preparer import DefaultRecordPreparer

class InMemoryDownloader(Downloader):
    def download_years(self, years, dest_dir, max_workers=1):
        # create fake tar.gz containing one CSV
        paths=[]
        for y in years:
            p = dest_dir/str(y)/f"{y}.tar.gz"
            p.parent.mkdir(parents=True, exist_ok=True)
            header = (
                '"STATION","DATE","LATITUDE","LONGITUDE","ELEVATION","NAME",'
                '"TEMP","TEMP_ATTRIBUTES","DEWP","DEWP_ATTRIBUTES","SLP","SLP_ATTRIBUTES",'
                '"STP","STP_ATTRIBUTES","VISIB","VISIB_ATTRIBUTES","WDSP","WDSP_ATTRIBUTES",'
                '"MXSPD","GUST","MAX","MAX_ATTRIBUTES","MIN","MIN_ATTRIBUTES",'
                '"PRCP","PRCP_ATTRIBUTES","SNDP","FRSHTT"\n'
            )
            row = (
                '"S","2020-01-01","0","0","0","N",'
                '"32","0","32","0","1000","0",'
                '"1000","0","10","0","5","0",'
                '"5","5","32","0","32","0",'
                '"0","","0","000000"\n'
            )
            content = (header + row).encode("utf-8")
            with tarfile.open(p, "w:gz") as tf:
                info = tarfile.TarInfo("data.csv")
                info.size = len(content)
                tf.addfile(info, io.BytesIO(content))
            paths.append(p)
        return paths

class InMemoryExtractor(ArchiveExtractor):
    def extract(self, archive_path, dest_dir):
        import tarfile
        dest_dir.mkdir(parents=True, exist_ok=True)
        extracted=[]
        with tarfile.open(archive_path, "r:gz") as tf:
            for m in tf.getmembers():
                f = tf.extractfile(m)
                out = dest_dir/m.name
                with open(out, "wb") as o:
                    o.write(f.read())
                extracted.append(out)
        return extracted

class DummyRepo:
    def __init__(self): self.docs=[]
    def bulk_insert(self, docs): self.docs.extend(docs)

def test_full_pipeline(tmp_path):
    cfg = type("C", (), {
        "DATA_DIR": tmp_path/"data",
        "DOWNLOAD_MAX_WORKERS": 1,
        "CHUNK_SIZE": 10
    })()
    logger = logging.getLogger("test_integration_pipeline")
    logger.setLevel(logging.INFO)
    downloader = InMemoryDownloader()
    extractor  = InMemoryExtractor()
    dl_step = DownloadStep(cfg, downloader, extractor, logger=logger)
    tf = ConcurrentTransformer(max_workers=1, logger=logger)
    tr_step = TransformStep(cfg, tf, logger=logger)
    repo = DummyRepo()
    loader = BatchLoader(DefaultRecordPreparer(logger),
                         repository=repo,
                         batch_size=10,
                         max_workers=1,
                         logger=logger)
    ld_step = LoadStep(cfg, loader, logger=logger)

    pipeline = Pipeline([dl_step, tr_step, ld_step])
    pipeline.run([2025])
    # after run, repo.docs should have at least one record
    assert repo.docs, "No docs loaded"
