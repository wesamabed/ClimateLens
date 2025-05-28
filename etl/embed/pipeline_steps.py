# etl/embed/pipeline_steps.py
from __future__ import annotations
import logging
from typing import Iterable, List, Mapping, Any, Optional

from etl.pipeline.protocols import Step
from etl.config import ETLConfig
from etl.embed.generator import EmbeddingGenerator

class EmbedStep(Step[Iterable[Mapping[str, Any]], List[Mapping[str, Any]]]):
    """Wraps the EmbeddingGenerator so it fits our Pipeline chain."""

    def __init__(
        self,
        cfg: ETLConfig,
        generator: EmbeddingGenerator,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.cfg = cfg
        self.generator = generator
        self.logger = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)

    def execute(self, docs: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        docs_list = list(docs)
        self.logger.debug(f"EmbedStep got {len(docs_list)} docs")
        return self.generator.transform(docs_list)


class IndexStep(Step[None, None]):
    """
    Ensures Atlas Vector index exists.
    Simple – only runs once per ETL run.
    """

    def __init__(self, index_builder, logger: logging.Logger) -> None:
        self.builder = index_builder
        self.logger = logger.getChild(self.__class__.__name__)

    def execute(self, _: None = None) -> None:
        self.logger.info("Ensuring Atlas Vector Search index")
        self.builder.ensure()
        return None
