from __future__ import annotations

import logging
from typing import Any

from app.config.settings import LLMSettings


logger = logging.getLogger(__name__)


class OpenAIService:
    """Small OpenAI chat service used by routing and answer generation."""

    def __init__(self, settings: LLMSettings | None = None) -> None:
        self.settings = settings or LLMSettings()
        if not self.settings.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install the openai package to use OpenAIService.") from exc

        self.client = OpenAI(api_key=self.settings.api_key, max_retries=self.settings.max_retries)
        self.last_prompt_messages: list[dict[str, str]] = []

    def generate(
        self,
        system_prompt: str,
        user_query: str,
        context: str = "",
        conversation_history: list[dict[str, str]] | None = None,
        temperature: float = 0.2,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        messages = self._build_messages(system_prompt, user_query, context, conversation_history or [])
        self.last_prompt_messages = messages
        logger.info(
            "LLM invocation | model=%s | messages=%s | task=%s",
            self.settings.model_name,
            len(messages),
            (metadata or {}).get("task", "answer_generation"),
        )
        try:
            response = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                temperature=temperature,
                timeout=self.settings.timeout_seconds,
            )
        except Exception:
            logger.exception("LLM failure")
            raise

        content = response.choices[0].message.content or ""
        return content.strip()

    def _build_messages(
        self,
        system_prompt: str,
        user_query: str,
        context: str,
        conversation_history: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]
        for item in conversation_history[-8:]:
            role = item.get("role", "")
            content = item.get("message") or item.get("content") or ""
            if role in {"user", "assistant"} and content.strip():
                messages.append({"role": role, "content": content.strip()})
        if context.strip():
            messages.append({"role": "system", "content": f"Retrieved context:\n{context.strip()}"})
        messages.append({"role": "user", "content": user_query})
        return messages
