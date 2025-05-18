# etl/pipeline/transform_step.py
from pathlib import Path
from typing import List
import logging

from etl.config import ETLConfig
from etl.transformer.protocols import Transformer
from etl.pipeline.protocols import Step

class TransformStep(Step[List[Path], List[dict]]):
    def __init__(
        self,
        config: ETLConfig,
        transformer: Transformer,
        logger: logging.Logger,
    ):
        self.config      = config
        self.transformer = transformer
        self.logger      = logger.getChild(self.__class__.__name__)

    def execute(self, paths: List[Path]) -> List[dict]:
        self.logger.info(f"Transforming {len(paths)} files")
        records = self.transformer.transform(paths)
        self.logger.info(f"TransformStep: {len(records)} records ready")
        return records
