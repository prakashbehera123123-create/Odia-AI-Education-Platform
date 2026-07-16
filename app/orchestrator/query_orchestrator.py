from __future__ import annotations
import logging
from typing import Any
from app.handlers import ConversationalHandler, EducationalHandler, GreetingHandler
from app.intent.intent_router import IntentRouter
from app.llm.openai_service import OpenAIService
from app.models import QueryResult
from app.retrieval.qdrant_retriever import QdrantRetriever
from rag.logging_config import configure_logging
from langsmith import traceable


configure_logging()
logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """Single runtime entry point for the Streamlit app and future APIs."""

    def __init__(
        self,
        intent_router: IntentRouter | None = None,
        educational_handler: EducationalHandler | None = None,
        conversational_handler: ConversationalHandler | None = None,
        greeting_handler: GreetingHandler | None = None,
        llm_service: OpenAIService | None = None,
        retriever: QdrantRetriever | None = None,
    ) -> None:
        self.llm_service = llm_service or OpenAIService()
        self.retriever = retriever or QdrantRetriever()
        self.intent_router = intent_router or IntentRouter(llm_service=self.llm_service)
        self.educational_handler = educational_handler or EducationalHandler(self.retriever, self.llm_service)
        self.conversational_handler = conversational_handler or ConversationalHandler(self.llm_service)
        self.greeting_handler = greeting_handler or GreetingHandler()
    @traceable(name = "query orchestrator")
    def ask(
        self,
        query: str,
        session_id: str | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        logger.info("Incoming query | session_id=%s | query=%s", session_id, query)
        try:
            intent = self.intent_router.classify(query)
            if intent == "greeting":
                answer = self.greeting_handler.handle(query)
                result = QueryResult(session_id=session_id, query=query, intent=intent, answer=answer)
            elif intent == "educational":
                answer = self.educational_handler.handle(query, conversation_history, top_k=top_k)
                result = QueryResult(
                    session_id=session_id,
                    query=query,
                    intent=intent,
                    answer=answer,
                    retrieved_chunks=self.educational_handler.last_retrieved_chunks,
                    context=self.educational_handler.last_context,
                    retrieval_debug=self.educational_handler.last_retrieval_debug,
                    prompt_preview=self.llm_service.last_prompt_messages,
                )
            elif intent == "conversational":
                answer = self.conversational_handler.handle(query, conversation_history)
                result = QueryResult(
                    session_id=session_id,
                    query=query,
                    intent=intent,
                    answer=answer,
                    prompt_preview=self.llm_service.last_prompt_messages,
                )
            else:
                result = QueryResult(
                    session_id=session_id,
                    query=query,
                    intent="out_of_scope",
                    answer=self._safe_out_of_scope_response(query),
                )
        except Exception:
            logger.exception("Routing failure")
            result = QueryResult(
                session_id=session_id,
                query=query,
                intent="out_of_scope",
                answer=self._safe_out_of_scope_response(query),
            )
        return result.as_dict()

    def close(self) -> None:
        self.retriever.close()

    def _safe_out_of_scope_response(self, query: str) -> str:
        if any("\u0b00" <= character <= "\u0b7f" for character in query):
            return "ମୁଁ ଏହି ଅନୁରୋଧରେ ସହାୟତା କରିପାରିବି ନାହିଁ। ଦୟାକରି ଏକ ପାଠ୍ୟ ବିଷୟର ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ।"
        return "I can’t help with that request. Please ask an educational question."
