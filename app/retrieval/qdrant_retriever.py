from __future__ import annotations

import logging
import re
from typing import Any
from langsmith import traceable

from app.config.settings import RetrievalSettings
from rag.embeddings.embedder import Embedder
from rag.vectordb.qdrant_store import QdrantStore


logger = logging.getLogger(__name__)


class QdrantRetriever:
    """Dense-vector retriever backed by BGE-M3 embeddings and local Qdrant."""

    _space_pattern = re.compile(r"[ \t]+")
    _newline_pattern = re.compile(r"\n{3,}")

    def __init__(self, settings: RetrievalSettings | None = None) -> None:
        self.settings = settings or RetrievalSettings()
        self.embedder = Embedder(self.settings.embedding_model)
        self.store = QdrantStore(
            db_path=self.settings.qdrant_db_path,
            collection_name=self.settings.collection_name,
            vector_dimension=self.settings.vector_dimension,
        )
        self.last_debug: dict[str, Any] = {}
        
    
    @traceable(name = "retriver time")
    def retrieve(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        clean_query = self._clean_query(query)
        try:
            query_vector = self.embedder.embed_text(clean_query)
            raw_results = self.store.search(query_vector, top_k=top_k or self.settings.top_k)
        except Exception:
            logger.exception("Retrieval failure")
            raise

        cleaned_results = [self._normalize_result(result) for result in raw_results]
        filtered = [result for result in cleaned_results if result["score"] >= self.settings.similarity_threshold]
        used_filter_fallback = False
        if cleaned_results and not filtered:
            filtered = cleaned_results[:1]
            used_filter_fallback = True

        deduped = self._dedupe(sorted(filtered, key=lambda item: item["score"], reverse=True))
        self.last_debug = {
            "query": clean_query,
            "total_retrieved": len(raw_results),
            "filtered_count": len(filtered),
            "deduped_count": len(deduped),
            "similarity_threshold": self.settings.similarity_threshold,
            "similarity_scores": [result["score"] for result in cleaned_results],
            "used_filter_fallback": used_filter_fallback,
        }
        logger.info("Retrieved chunk count | count=%s", len(deduped))
        return deduped

    def close(self) -> None:
        self.store.close()

    def _clean_query(self, query: str) -> str:
        return self._space_pattern.sub(" ", query.strip())

    def _normalize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        payload = dict(result.get("payload") or {})
        text = str(payload.get("text") or "")
        text = self._space_pattern.sub(" ", text.strip())
        text = self._newline_pattern.sub("\n\n", text)
        return {
            "score": float(result.get("score", 0.0)),
            "payload": {
                "text": text,
                "class": payload.get("class"),
                "subject": payload.get("subject"),
                "book": payload.get("book"),
                "chapter": payload.get("chapter"),
                "page": payload.get("page"),
                "source_file": payload.get("source_file"),
                "chunk_index": payload.get("chunk_index"),
            },
        }

    def _dedupe(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[Any, Any, Any, str]] = set()
        deduped: list[dict[str, Any]] = []
        for result in results:
            payload = result["payload"]
            key = (
                payload.get("source_file"),
                payload.get("page"),
                payload.get("chunk_index"),
                payload.get("text", "")[:160],
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(result)
        return deduped
