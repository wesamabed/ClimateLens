# etl/main.py
import argparse
from pathlib import Path
from etl.config import ETLConfig
from etl.logger import get_logger
from etl.pipeline.steps import DownloadStep, TransformStep, LoadStep

def parse_args():
    parser = argparse.ArgumentParser(description="NOAA GSOD ETL pipeline")
    parser.add_argument("--dry-run",   action="store_true", help="Skip DB writes")
    parser.add_argument("--uri",       type=str,             help="Override MONGODB_URI")
    parser.add_argument("--log-level", default="INFO",       help="Logging level")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = get_logger("etl.main", level=args.log_level)

    # Build config overrides
    overrides = {}
    if args.uri:
        overrides["MONGODB_URI"] = args.uri
    elif args.dry_run:
        logger.warning("Dry-run mode: using placeholder URI")
        overrides["MONGODB_URI"] = "mongodb://dry-run-placeholder"

    # Load & validate config (Factory + DIP)
    cfg = ETLConfig(**overrides)

    # Ensure data directory
    Path(cfg.DATA_DIR).mkdir(parents=True, exist_ok=True)
    logger.info("Configuration loaded: %s", cfg.model_dump())

    # Strategy: run through each pipeline step
    steps = [DownloadStep(cfg), TransformStep(cfg), LoadStep(cfg)]
    for step in steps:
        logger.info("=== Running step: %s ===", step.__class__.__name__)
        step.execute()

    if args.dry_run:
        logger.info("Dry-run complete; exiting without DB actions")

if __name__ == "__main__":
    main()
