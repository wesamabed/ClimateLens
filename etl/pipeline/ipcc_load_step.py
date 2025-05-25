from typing import List, Dict, Any, Optional
import logging
from etl.pipeline.protocols import Step
from etl.config import ETLConfig
from etl.loader.loader import BatchLoader   # ← already written earlier

class IPCCLoadStep(Step[List[Dict[str, Any]], None]):
    def __init__(self, cfg: ETLConfig, loader: BatchLoader, logger: Optional[logging.Logger]=None):
        self.cfg, self.loader = cfg, loader
        self.logger = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)

    def execute(self, docs: List[Dict[str, Any]]) -> None:
        self.logger.info(f"Loading {len(docs)} report chunks")
        self.loader.load(docs)
        self.logger.info("LoadStep complete")
