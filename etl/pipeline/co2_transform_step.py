from typing import Iterable, List, Mapping, Any, Optional
import logging

from etl.pipeline.protocols import Step
from etl.config import ETLConfig
from etl.transformer.co2_transformer import CO2Transformer

class CO2TransformStep(Step[List[Mapping[str,Any]], List[Mapping[str,Any]]]):
    """
    Wraps a CO2Transformer so it can be slotted into our Pipeline.
    Input: list of raw JSON records
    Output: list of flat dicts ready for loading
    """
    def __init__(
        self,
        config: ETLConfig,
        transformer: CO2Transformer,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.config      = config
        self.transformer = transformer
        self.logger      = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)

    def execute(self, records: Iterable[Mapping[str,Any]]) -> List[Mapping[str,Any]]:
        recs = list(records)
        self.logger.info(f"Transforming {len(recs)} CO₂ records")
        try:
            transformed = self.transformer.transform(recs)
            return transformed
        except Exception:
            # log full stack if something truly unexpected happens
            self.logger.exception("Unexpected failure in CO₂ transform")
            raise
