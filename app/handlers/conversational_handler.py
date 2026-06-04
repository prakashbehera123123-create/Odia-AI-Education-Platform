from __future__ import annotations

import logging

from app.llm.openai_service import OpenAIService
from app.prompts import CONVERSATIONAL_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class ConversationalHandler:
    def __init__(self, llm_service: OpenAIService) -> None:
        self.llm_service = llm_service

    def handle(self, query: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        return self.llm_service.generate(
            system_prompt=CONVERSATIONAL_SYSTEM_PROMPT,
            user_query=query,
            conversation_history=conversation_history or [],
            metadata={"task": "conversational_response"},
        )
