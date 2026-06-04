from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class QueryResult:
    session_id: str | None
    query: str
    intent: str
    answer: str
    retrieved_chunks: list[dict[str, Any]] = field(default_factory=list)
    context: str = ""
    retrieval_debug: dict[str, Any] = field(default_factory=dict)
    prompt_preview: list[dict[str, str]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "query": self.query,
            "intent": self.intent,
            "answer": self.answer,
            "retrieved_chunks": self.retrieved_chunks,
            "context": self.context,
            "retrieval_debug": self.retrieval_debug,
            "prompt_preview": self.prompt_preview,
        }
