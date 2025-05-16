import argparse
from pathlib import Path
from etl.config import ETLConfig
from etl.logger import get_logger
from etl.pipeline.steps import DownloadStep, TransformStep, LoadStep

def parse_args():
    p = argparse.ArgumentParser(description="NOAA GSOD ETL pipeline")
    p.add_argument("--dry-run",    action="store_true", help="Skip DB writes")
    p.add_argument("--uri",        type=str,             help="Override MONGODB_URI")
    p.add_argument("--log-level",  default="INFO",       help="Logging level")
    return p.parse_args()

def main():
    args = parse_args()
    logger = get_logger(__name__, args.log_level)

    # ① Build overrides (SRP)
    overrides = {}
    if args.uri:
        overrides["MONGODB_URI"] = args.uri
    elif args.dry_run:
        placeholder = "mongodb://dry-run-placeholder-0000"
        logger.warning("Dry-run: using placeholder URI")
        overrides["MONGODB_URI"] = placeholder

    # ② Load & validate config (Factory + DIP)
    cfg = ETLConfig(**overrides)

    # ③ Ensure data directory exists
    Path(cfg.DATA_DIR).mkdir(parents=True, exist_ok=True)

    logger.info("Configuration loaded: %s", cfg.model_dump())

    # ④ Execute pipeline (Strategy)
    steps = [DownloadStep(cfg), TransformStep(cfg), LoadStep(cfg)]
    for step in steps:
        logger.info("Starting step: %s", step.__class__.__name__)
        step.execute()

    if args.dry_run:
        logger.info("Dry-run complete; no data was written.")

if __name__ == "__main__":
    main()
