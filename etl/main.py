import argparse

from etl.config import get_config
from etl.logger import get_logger
from etl.pipeline.pipeline import Pipeline
from etl.embed.text_index import AtlasTextIndexBuilder


# GSOD imports
from etl.downloader.http_downloader import HTTPDownloader
from etl.downloader.tar_extractor import TarExtractor
from etl.pipeline.download_step import DownloadStep
from etl.pipeline.transform_step import TransformStep
from etl.pipeline.load_step import LoadStep
from etl.transformer.concurrent import ConcurrentTransformer
from etl.loader.loader import BatchLoader
from etl.loader.preparer import DefaultRecordPreparer
from etl.loader.repository import MongoRepository

# CO₂ imports
from etl.downloader.co2_downloader import CO2Downloader
from etl.pipeline.co2_download_step import CO2DownloadStep
from etl.transformer.co2_transformer import CO2Transformer
from etl.pipeline.co2_transform_step import CO2TransformStep
from etl.loader.emissions_repository import EmissionsRepository

# IPCC imports
from etl.downloader.pdf_downloader import PDFDownloader
from etl.pipeline.ipcc_download_step import IPCCDownloadStep
from etl.transformer.ipcc_transformer import IPCCTransformer
from etl.pipeline.ipcc_load_step import IPCCLoadStep
from etl.loader.reports_repository import ReportsRepository
from etl.pipeline.ipcc_transform_step import IPCCTransformStep
from etl.loader.IdentityPreparer import IdentityPreparer

# Embedding imports
from etl.embed.vertex_client import VertexEmbeddingClient
from etl.embed.pipeline_steps import EmbedStep
from etl.embed.pipeline_steps import IndexStep
from etl.embed.generator import EmbeddingGenerator


def parse_args():
    p = argparse.ArgumentParser("ClimateLens ETL")
    # GSOD flags
    p.add_argument("--start-year", type=int, help="first GSOD year to fetch")
    p.add_argument("--end-year",   type=int, help="last GSOD year to fetch")
    # CO₂ flags
    p.add_argument("--co2-start-year", type=int, help="first CO₂ year to fetch")
    p.add_argument("--co2-end-year",   type=int, help="last CO₂ year to fetch")

    # ipcc flags
    p.add_argument("--skip-ipcc",  action="store_true", help="don’t run the IPCC (report) pipeline")
    p.add_argument("--ipcc-pdf-url",   type=str, help="override IPCC PDF download URL")
    p.add_argument("--ipcc-chunk-words", type=int, help="override max words per chunk")
    p.add_argument("--ipcc-pdf-name", type=str, help="override IPCC PDF file name")

    # Common ETL flags
    p.add_argument("--uri",        type=str, help="override MONGODB_URI")
    p.add_argument("--db-name",    type=str, help="override DB_NAME")
    p.add_argument("--data-dir",   type=str, help="override local data directory")
    p.add_argument("--data-dir-ipcc", type=str, help="override local IPCC data directory")
    p.add_argument("--chunk-size", type=int, help="override batch size for loading")
    p.add_argument("--download-base-url",       type=str, help="override GSOD download base URL")
    p.add_argument("--download-retry-attempts", type=int, help="override download retry attempts")
    p.add_argument("--download-retry-wait",     type=int, help="override download retry wait seconds")
    p.add_argument("--download-max-workers",    type=int, help="override download maximum workers")
    p.add_argument("--load-max-workers",        type=int, help="override load maximum workers")
    p.add_argument("--log-level",  default="INFO", help="logging level")
    p.add_argument("--dry-run",    action="store_true", help="skip any DB writes")
    p.add_argument("--skip-gsod",  action="store_true", help="don’t run the GSOD pipeline")
    p.add_argument("--skip-co2",   action="store_true", help="don’t run the CO₂ pipeline")
    p.add_argument("--skip-embed", action="store_true")
    p.add_argument("--embed-batch-size", type=int)
    p.add_argument("--vertex-project", type=str)
    p.add_argument("--vertex-region", type=str)
    p.add_argument("--vertex-model", type=str)
    p.add_argument("--reindex", action="store_true")

    return p.parse_args()


def main():
    args   = parse_args()
    logger = get_logger("etl.main", level=args.log_level)

    # build our unified config
    cfg = get_config(
        uri=args.uri,
        db_name=args.db_name,
        data_dir=args.data_dir,
        data_dir_ipcc=args.data_dir_ipcc,
        chunk_size=args.chunk_size,
        start_year=args.start_year,
        end_year=args.end_year,
        co2_start_year=args.co2_start_year,
        co2_end_year=args.co2_end_year,
        download_base_url=args.download_base_url,
        download_retry_attempts=args.download_retry_attempts,
        download_retry_wait=args.download_retry_wait,
        download_max_workers=args.download_max_workers,
        load_max_workers=args.load_max_workers,
        skip_gsod=args.skip_gsod,
        skip_co2=args.skip_co2,
        ipcc_pdf_url=args.ipcc_pdf_url,
        ipcc_pdf_name=args.ipcc_pdf_name,  
        ipcc_chunk_words=args.ipcc_chunk_words,
        skip_ipcc=args.skip_ipcc,
        skip_embed=args.skip_embed,
        embed_batch_size=args.embed_batch_size,
        vertex_project=args.vertex_project,
        vertex_region=args.vertex_region,
        vertex_model=args.vertex_model,
        reindex=args.reindex,
    )

    # ── GSOD pipeline ─────────────────────────────────────────────────────────────
    if not cfg.SKIP_GSOD:
        # 1) build the full list of candidate years
        all_gsod_years = list(range(cfg.START_YEAR, cfg.END_YEAR + 1))

        # 2) split into “already in Mongo” vs “to process”
        if args.dry_run:
            gsod_loaded = []
            gsod_to_process = all_gsod_years
        else:
            repo = MongoRepository(cfg, logger)
            gsod_loaded = [y for y in all_gsod_years if repo.count_for_year(y) > 0]
            gsod_to_process = [y for y in all_gsod_years if y not in gsod_loaded]

        logger.info(f"Skipping already-loaded GSOD years: {gsod_loaded}")
        logger.info(f"Will process GSOD years: {gsod_to_process}")

        # 3) if there’s nothing left, bail out early
        if not gsod_to_process:
            logger.info("No new GSOD years to ingest; skipping GSOD pipeline.")
        else:
            # 4) wire up your steps to only run on gsod_to_process
            gsod_downloader = HTTPDownloader(
                base_url=cfg.DOWNLOAD_BASE_URL,
                retry_attempts=cfg.DOWNLOAD_RETRY_ATTEMPTS,
                retry_wait=cfg.DOWNLOAD_RETRY_WAIT,
                logger=logger,
            )
            gsod_extractor  = TarExtractor(logger)
            gsod_download   = DownloadStep(cfg, gsod_downloader, gsod_extractor, logger)

            gsod_transformer = ConcurrentTransformer(
                max_workers=cfg.DOWNLOAD_MAX_WORKERS,
                logger=logger,
            )
            gsod_transform   = TransformStep(cfg, gsod_transformer, logger)

            steps = [gsod_download, gsod_transform]
            if not args.dry_run:
                preparer = DefaultRecordPreparer(logger)
                loader   = BatchLoader(
                    preparer=preparer,
                    repository=repo,
                    batch_size=cfg.CHUNK_SIZE,
                    max_workers=cfg.LOAD_MAX_WORKERS,
                    logger=logger,
                )
                steps.append(LoadStep(cfg, loader, logger))

            logger.info("Starting GSOD pipeline")
            Pipeline(steps).run(initial_input=gsod_to_process)
            logger.info("GSOD pipeline complete")
    else:
        logger.info("Skipping GSOD pipeline")

    # ── CO₂ pipeline ────────────────────────────────────────────────────────────────
    if not cfg.SKIP_CO2:
       # pick the years
       all_co2_years = list(range(cfg.CO2_START_YEAR, cfg.CO2_END_YEAR + 1))
       logger.info(f"→ CO₂ pipeline: years {all_co2_years}")

       # skip any already in Mongo
       if not args.dry_run:
           em_repo = EmissionsRepository(cfg, logger)
           loaded = [y for y in all_co2_years if em_repo.count_for_year(y) > 0]
           to_do  = [y for y in all_co2_years if y not in loaded]
           logger.info(f"Skipping already-loaded CO₂ years: {loaded}")
       else:
           to_do = all_co2_years

       if not to_do:
           logger.info("Nothing to do; all requested CO₂ years are already ingested.")
       else:
           # Download
           co2_downloader = CO2Downloader(
               indicator=cfg.CO2_INDICATOR,
               retry_attempts=cfg.DOWNLOAD_RETRY_ATTEMPTS,
               retry_wait=cfg.DOWNLOAD_RETRY_WAIT,
               logger=logger,
           )
           co2_dl_step = CO2DownloadStep(cfg, co2_downloader, logger)

           # Transform
           co2_transformer = CO2Transformer(logger)
           co2_xform_step = CO2TransformStep(cfg, co2_transformer, logger)

           steps = [co2_dl_step, co2_xform_step]

           # Load (unless dry‐run)
           if not args.dry_run:
               prep   = DefaultRecordPreparer(logger)
               loader = BatchLoader(
                   preparer=prep,
                   repository=em_repo,
                   batch_size=cfg.CHUNK_SIZE,
                   max_workers=cfg.LOAD_MAX_WORKERS,
                   logger=logger,
               )
               load_step = LoadStep(cfg, loader, logger)
               steps.append(load_step)

           logger.info("Starting CO₂ pipeline")
           Pipeline(steps).run(initial_input=to_do)
           logger.info("CO₂ pipeline complete")
    else:
       logger.info("Skipping CO₂ pipeline")

    # ── IPCC pipeline ────────────────────────────────────────────────────────────────
    if not cfg.SKIP_IPCC:
        logger.info("→ IPCC AR6 SPM pipeline")
    
        pdf_downloader = PDFDownloader(
            url=cfg.IPCC_PDF_URL,
            dest_dir=cfg.DATA_DIR_IPCC,
            retry_attempts=cfg.DOWNLOAD_RETRY_ATTEMPTS,
            retry_wait=cfg.DOWNLOAD_RETRY_WAIT,
            logger=logger,
        )
        ipcc_download  = IPCCDownloadStep(cfg, pdf_downloader, logger)
    
        ipcc_transformer = IPCCTransformer(logger)
        ipcc_transform   = IPCCTransformStep(cfg, ipcc_transformer, logger)   # re-use generic transform step pattern
    
        ipcc_steps = [ipcc_download, ipcc_transform]
    
        if not args.dry_run:
            reports_repo = ReportsRepository(cfg, logger)
            preparer = IdentityPreparer(logger)
            batch_loader = BatchLoader(
                preparer=preparer,         
                repository=reports_repo,
                batch_size=cfg.CHUNK_SIZE,
                max_workers=cfg.LOAD_MAX_WORKERS,
                logger=logger,
            )
            ipcc_steps.append(IPCCLoadStep(cfg, batch_loader, logger))
    
        logger.info("Starting IPCC pipeline")
        Pipeline(ipcc_steps).run()
        logger.info("IPCC pipeline complete")
    else:
        logger.info("Skipping IPCC pipeline")

    # ── EMBED pipeline ─────────────────────────────────────────────
    if cfg.SKIP_EMBED and not args.reindex:
        logger.info("Skipping Embedding pipeline (SKIP_EMBED=true and --reindex not requested)")
    else:
        logger.info("→ Embedding pipeline")

        # 1. Pull paragraphs without embedding
        repo = ReportsRepository(cfg, logger)
        todo = list(repo.col.find({"embedding": {"$exists": False}}, {"_id": 0, "section": 1, "paragraph": 1, "text": 1}))
        steps: list = []

        # ── (A) embed if needed ────────────────────────────────────
        if not cfg.SKIP_EMBED and todo:
            logger.info(f"{len(todo)} paragraphs need embeddings")
            client = VertexEmbeddingClient(
                project=cfg.VERTEX_PROJECT,
                region=cfg.VERTEX_REGION,
                model_name=cfg.VERTEX_MODEL,
                logger=logger,
            )
            generator  = EmbeddingGenerator(client, cfg.EMBED_BATCH_SIZE, logger)
            steps.append(EmbedStep(cfg, generator, logger))

            if not args.dry_run:
                steps.append(
                    LoadStep(
                        cfg,
                        BatchLoader(
                            preparer=IdentityPreparer(logger),
                            repository=repo,
                            batch_size=cfg.CHUNK_SIZE,
                            max_workers=cfg.LOAD_MAX_WORKERS,
                            logger=logger,
                            insert_fn=repo.bulk_upsert_embeddings,
                        ),
                        logger,
                    )
                )
        elif cfg.SKIP_EMBED:
            logger.info("SKIP_EMBED=true → skipping new embeddings")
        else:
            logger.info("All paragraphs already embedded.")

        # ── (B) always rebuild indexes when --reindex is given ─────
        if args.reindex:
            if not cfg.ATLAS_PROJECT_ID:
                logger.warning("--reindex ignored → Atlas API keys not configured")
            else:
                from etl.embed.atlas_index import AtlasIndexBuilder
                vector_builder = AtlasIndexBuilder(
                    proj_id=cfg.ATLAS_PROJECT_ID,
                    cluster=cfg.ATLAS_CLUSTER,
                    public_key=cfg.ATLAS_PUBLIC_KEY,
                    private_key=cfg.ATLAS_PRIVATE_KEY,
                    logger=logger,
                )
                steps.append(IndexStep(vector_builder, logger))
                # 2) Full‐text index on reports.text
                text_builder = AtlasTextIndexBuilder(
                    mongo_uri   = cfg.MONGODB_URI,
                    proj_id     = cfg.ATLAS_PROJECT_ID,
                    cluster     = cfg.ATLAS_CLUSTER,
                    public_key  = cfg.ATLAS_PUBLIC_KEY,
                    private_key = cfg.ATLAS_PRIVATE_KEY,
                    db_name     = cfg.DB_NAME,
                    coll_name   = "reports",
                    logger      = logger,
                )
                text_builder._ensure_text_index()

                # 3) Geospatial index on weather.location
                weather_repo = MongoRepository(cfg, logger)
                weather_repo.ensure_geo_index()

        # run the mini-pipeline only if we actually have work to do
        if steps:
            Pipeline(steps).run(initial_input=todo)
        else:
            logger.info("Nothing to embed or index – skipping Embedding pipeline")
    
    logger.info("ETL run complete")

if __name__ == "__main__":
    main()
