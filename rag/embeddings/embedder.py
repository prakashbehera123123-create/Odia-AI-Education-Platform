from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from configs.settings import EMBEDDING_MODEL


class Embedder:
    """Small wrapper around SentenceTransformer for normalized embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        embeddings = self.embed_batch([text])
        return embeddings[0]

    def embed_batch(self, texts: Sequence[str], batch_size: int = 16) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            list(texts),
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        normalized = self._normalize(embeddings)
        return normalized.astype(float).tolist()

    @staticmethod
    def _normalize(embeddings: np.ndarray) -> np.ndarray:
        array = np.asarray(embeddings, dtype=np.float32)
        if array.ndim == 1:
            array = array.reshape(1, -1)

        norms = np.linalg.norm(array, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return array / norms
