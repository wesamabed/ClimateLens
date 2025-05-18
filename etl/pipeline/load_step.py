# etl/pipeline/load_step.py
from typing import List, Dict, Any
import logging

from etl.config import ETLConfig
from etl.loader.protocols import Loader
from etl.pipeline.protocols import Step

class LoadStep(Step[List[Dict[str,Any]], None]):
    def __init__(
        self,
        config: ETLConfig,
        loader: Loader,
        logger: logging.Logger,
    ):
        self.config = config
        self.loader = loader
        self.logger = logger.getChild(self.__class__.__name__)

    def execute(self, records: List[Dict[str,Any]]) -> None:
        self.logger.info(f"Loading {len(records)} records")
        self.loader.load(records)
        self.logger.info("LoadStep complete")
