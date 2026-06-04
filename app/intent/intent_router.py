from __future__ import annotations

import logging
from collections.abc import Callable

from app.llm.openai_service import OpenAIService
from app.prompts import INTENT_ROUTER_SYSTEM_PROMPT


SUPPORTED_INTENTS = {"greeting", "educational", "conversational", "out_of_scope"}
logger = logging.getLogger(__name__)


class IntentRouter:
    """LLM-backed intent router with strict label normalization."""

    def __init__(
        self,
        llm_service: OpenAIService | None = None,
        classifier: Callable[[str], str] | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.classifier = classifier

    def classify(self, query: str) -> str:
        if not query.strip():
            return "out_of_scope"

        try:
            raw_label = self._classify_with_llm(query)
            label = self._normalize_label(raw_label)
        except Exception:
            logger.exception("Routing failure")
            label = "out_of_scope"

        logger.info("Predicted intent | intent=%s", label)
        return label

    def _classify_with_llm(self, query: str) -> str:
        if self.classifier is not None:
            return self.classifier(query)
        if self.llm_service is None:
            raise ValueError("IntentRouter requires an OpenAIService or classifier.")
        return self.llm_service.generate(
            system_prompt=INTENT_ROUTER_SYSTEM_PROMPT,
            user_query=query,
            temperature=0.0,
            metadata={"task": "intent_classification"},
        )

    def _normalize_label(self, raw_label: str) -> str:
        label = raw_label.strip().lower()
        label = label.replace("`", "").replace('"', "").replace("'", "")
        label = label.split()[0] if label else ""
        return label if label in SUPPORTED_INTENTS else "out_of_scope"
