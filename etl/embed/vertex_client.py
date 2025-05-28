"""
Vertex AI text-embedding helper
──────────────────────────────
• Handles project / region init
• Retries on transient Google errors (5xx, deadline)
• Returns pure-Python float lists so they can be stored in Mongo
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

import vertexai                              
from vertexai.language_models import TextEmbeddingModel
from google.api_core import exceptions as gexc
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class VertexEmbeddingClient:
    """
    Parameters
    ----------
    project   : GCP project ID that owns Vertex AI
    region    : Vertex AI region (default ``us-central1``)
    model_name: Vertex model string; defaults to Google's Gecko
    dims      : Expected dimensionality; we raise if it changes
    """

    def __init__(
        self,
        project: str,
        region: str = "us-central1",
        model_name: str = "gemini-embedding-001",
        dims: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        vertexai.init(project=project, location=region)

        self._model: TextEmbeddingModel = TextEmbeddingModel.from_pretrained(model_name)
        self.dims = dims
        self.logger = logger

        self.logger.info(
            "Vertex client initialised – project=%s region=%s model=%s",
            project,
            region,
            model_name,
        )

    # ── public API ────────────────────────────────────────────────────────

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return an embedding vector for every input text."""
        if not texts:
            return []
        return self._call_with_retry(texts)

    # ── internal helper with robust retry ────────────────────────────────

    @retry(
        retry=retry_if_exception_type(
            (gexc.ServiceUnavailable, gexc.DeadlineExceeded, gexc.InternalServerError)
        ),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _call_with_retry(self, texts: List[str]) -> List[List[float]]:
        self.logger.debug("Vertex → embedding %s texts", len(texts))
        call_tic = time.perf_counter()
        embeddings = self._model.get_embeddings(texts)  # list[Embedding]
        self.logger.debug(
            f"Vertex ← {len(embeddings)} vecs in {time.perf_counter()-call_tic:.2f}s"
        )
        vectors = [e.values for e in embeddings]

                # ── auto-detect dims on first batch ────────────────────────────
        if self.dims is None:
            self.dims = len(vectors[0])
            self.logger.info(f"Embedding dimension auto-set to {self.dims}")

        for v in vectors:
            if len(v) != self.dims:  # safety-belt
                raise ValueError(
                    f"Expected {self.dims}-d vectors, got {len(v)} – "
                    "check model version"
                )
        self.logger.debug("Vertex ← OK")
        return vectors
