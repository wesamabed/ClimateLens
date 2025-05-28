"""
EmbeddingGenerator
──────────────────
Batches paragraph docs → calls VertexEmbeddingClient → returns docs + 'embedding'.
"""
from __future__ import annotations

import logging
import time
from typing import Any, List, Mapping

from etl.transformer.protocols import Transformer
from .vertex_client import VertexEmbeddingClient


class EmbeddingGenerator(Transformer):
    def __init__(
        self,
        client: VertexEmbeddingClient,
        batch_size: int = 1,
        logger: logging.Logger | None = None,
    ) -> None:
        self.client = client
        self.batch_size = max(1, batch_size)
        self.logger = (logger or logging.getLogger(__name__)).getChild(
            self.__class__.__name__
        )

    # ------------------------------------------------------------------ #
    def transform(self, records: List[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        total = len(records)
        if total == 0:
            self.logger.info("No paragraphs to embed; skipping.")
            return []

        self.logger.info(
            f"Embedding {total:,} paragraphs "
            f"(batch={self.batch_size}, model={self.client._model})"
        )

        t0 = time.perf_counter()
        successes = failures = 0
        out: list[dict[str, Any]] = []

        for batch_idx, start in enumerate(range(0, total, self.batch_size), 1):
            chunk = records[start : start + self.batch_size]
            texts = [c["text"] for c in chunk]

            tic = time.perf_counter()
            vecs = None # Initialize vecs to None for current batch
            
            try:
                vecs = self.client.embed_batch(texts)
            except Exception as exc:
                # Log the error, but don't 'continue' immediately
                self.logger.error(
                    f"Batch {batch_idx} FAILED "
                    f"({len(chunk)} docs, offset {start}-{start+len(chunk)-1}): {exc!r}"
                )
                # Failures will be incremented after 'toc' is set
            
            # This line will ALWAYS execute, even if an exception occurred
            toc = time.perf_counter() 
            duration = toc - tic # Calculate duration after toc is guaranteed to be set

            if vecs is None: # Check if the embedding call failed
                failures += len(chunk) # Increment failures here
                self.logger.info( # Log the duration even for failed batches
                    f"Batch {batch_idx:>3} failed in {duration:5.2f}s."
                )
                continue # Now, safely move to the next batch

            # Attach vectors (only if vecs was successfully populated)
            for doc, vec in zip(chunk, vecs):
                enriched = dict(doc)
                enriched["embedding"] = vec
                out.append(enriched)
            successes += len(chunk)

            # ── verbose progress log ─────────────────────────────────── #
            pct = (min(start + len(chunk), total) / total) * 100
            self.logger.info(
                f" Batch {batch_idx:>3}: {len(chunk):>4} docs "
                f"| {duration:5.2f}s | progress {pct:5.1f}%"
            )
            # Show a tiny sample of the first vector for sanity checks
            if vecs:
                self.logger.debug(
                    f"    sample dims: {vecs[0][:3]} … ({len(vecs[0])}-d)"
                )

        elapsed = time.perf_counter() - t0
        self.logger.info(
            f"Embedding complete in {elapsed:,.1f}s – "
            f"success {successes}/{total}, failed {failures}"
        )
        return out