import argparse
from etl.config import get_config
from etl.logger import get_logger
from etl.pipeline.pipeline import Pipeline
from etl.pipeline.download_step import DownloadStep
from etl.pipeline.transform_step import TransformStep
from etl.pipeline.load_step import LoadStep

from etl.downloader.ftp_downloader import FTPDownloader
from etl.downloader.tar_extractor import TarExtractor
from etl.transformer.concurrent import ConcurrentTransformer
from etl.loader.loader import BatchLoader
from etl.loader.preparer   import DefaultRecordPreparer
from etl.loader.repository import MongoRepository

def parse_args():
    parser = argparse.ArgumentParser("NOAA GSOD ETL")
    parser.add_argument("--start-year", type=int, help="first year to fetch")
    parser.add_argument("--end-year",   type=int, help="last year to fetch")
    parser.add_argument("--uri",        type=str, help="override MONGODB_URI")
    parser.add_argument("--db-name",    type=str, help="override DB_NAME")
    parser.add_argument("--chunk-size", type=int, help="override batch size for loading")
    parser.add_argument("--data-dir",   type=str, help="override local data directory")
    parser.add_argument("--ftp-retry-attempts", type=int, help="override FTP retry attempts")
    parser.add_argument("--ftp-retry-wait",     type=int, help="override FTP retry wait seconds")
    parser.add_argument("--ftp-max-workers",    type=int, help="override FTP maximum workers")
    parser.add_argument("--log-level",  default="INFO", help="logging level")
    parser.add_argument("--dry-run", action="store_true", help="skip DB load")
    return parser.parse_args()

def main():
    args   = parse_args()
    logger = get_logger("etl.main", level=args.log_level)
    cfg    = get_config(
        uri=args.uri,
        start_year=args.start_year,
        end_year=args.end_year,
        db_name=args.db_name,
        data_dir=args.data_dir,
        chunk_size=args.chunk_size,
        ftp_retry_attempts=args.ftp_retry_attempts,
        ftp_retry_wait=args.ftp_retry_wait,
        ftp_max_workers=args.ftp_max_workers,
    )

    # Initialize dependencies for each step.
    downloader = FTPDownloader(host = cfg.FTP_HOST,user = cfg.FTP_USER,
                               passwd = cfg.FTP_PASS,retry_attempts = cfg.FTP_RETRY_ATTEMPTS,
                               retry_wait = cfg.FTP_RETRY_WAIT,logger = logger,)
    extractor   = TarExtractor(logger)
    transformer = ConcurrentTransformer(max_workers=cfg.FTP_MAX_WORKERS, logger=logger,)
    preparer   = DefaultRecordPreparer(logger)
    repository = MongoRepository(cfg, logger)
    loader     = BatchLoader(preparer=preparer,repository=repository,batch_size=cfg.CHUNK_SIZE,max_workers=cfg.FTP_MAX_WORKERS,logger=logger,)

    # Build the pipeline steps based on the new pipeline structure.
    steps = [
        DownloadStep(cfg, downloader, extractor, logger),
        TransformStep(cfg, transformer, logger),
    ]
    
    # Only add the LoadStep if not in dry-run mode.
    if not args.dry_run:
        steps.append( LoadStep(cfg, loader, logger) )

    pipeline = Pipeline(steps)
    pipeline.run()

if __name__ == "__main__":
    main()