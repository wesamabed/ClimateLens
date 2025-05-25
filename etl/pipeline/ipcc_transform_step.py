from typing import List, Dict, Any, Optional
import logging
from etl.pipeline.protocols import Step
from etl.transformer.protocols import Transformer
from etl.config import ETLConfig

class IPCCTransformStep(Step[List[str], List[Dict[str, Any]]]):  # input = list[Path]
    def __init__(self, cfg: ETLConfig, transformer: Transformer,
                 logger: Optional[logging.Logger] = None):
        self.cfg, self.transformer = cfg, transformer
        self.logger = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)

    def execute(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        self.logger.info(f"Transforming {len(pdf_paths)} PDF(s)")
        return self.transformer.transform(pdf_paths)
