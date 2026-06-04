from __future__ import annotations

import logging
import re
from typing import Any

from app.config.settings import ContextSettings
from app.llm.openai_service import OpenAIService
from app.prompts.prompts import EDUCATIONAL_FALLBACK_RESPONSE, EDUCATIONAL_SYSTEM_PROMPT
from app.retrieval.qdrant_retriever import QdrantRetriever


logger = logging.getLogger(__name__)


class EducationalHandler:
    """Runs retrieval, context building, and answer generation for academic queries."""

    _space_pattern = re.compile(r"[ \t]+")
    _newline_pattern = re.compile(r"\n{3,}")

    def __init__(
        self,
        retriever: QdrantRetriever,
        llm_service: OpenAIService,
        context_settings: ContextSettings | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm_service = llm_service
        self.context_settings = context_settings or ContextSettings()
        self.last_retrieved_chunks: list[dict[str, Any]] = []
        self.last_context = ""
        self.last_retrieval_debug: dict[str, Any] = {}

    def handle(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
        top_k: int | None = None,
    ) -> str:
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)
        context = self.build_context(retrieved_chunks)
        self.last_retrieved_chunks = retrieved_chunks
        self.last_context = context
        self.last_retrieval_debug = self.retriever.last_debug

        if not context.strip():
            return EDUCATIONAL_FALLBACK_RESPONSE

        answer = self.llm_service.generate(
            system_prompt=EDUCATIONAL_SYSTEM_PROMPT,
            user_query=query,
            context=context,
            conversation_history=conversation_history or [],
            metadata={"task": "educational_rag"},
        )
        return answer or EDUCATIONAL_FALLBACK_RESPONSE

    def build_context(self, retrieved_chunks: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            payload = chunk.get("payload") or {}
            text = self._clean_text(str(payload.get("text") or ""))
            if not text:
                continue
            metadata = self._format_metadata(payload)
            chunk_text = f"[Chunk {index}]\n{metadata}\n{text}" if metadata else f"[Chunk {index}]\n{text}"
            parts.append(chunk_text.strip())

        context = "\n\n".join(parts)
        return context[: self.context_settings.max_context_length].rstrip()

    def _clean_text(self, text: str) -> str:
        text = self._space_pattern.sub(" ", text.strip())
        return self._newline_pattern.sub("\n\n", text)

    def _format_metadata(self, payload: dict[str, Any]) -> str:
        fields = {
            "class": payload.get("class"),
            "subject": payload.get("subject"),
            "book": payload.get("book"),
            "chapter": payload.get("chapter"),
            "page": payload.get("page"),
            "source_file": payload.get("source_file"),
        }
        values = [f"{key}: {value}" for key, value in fields.items() if value not in (None, "")]
        return "Metadata: " + ", ".join(values) if values else ""
