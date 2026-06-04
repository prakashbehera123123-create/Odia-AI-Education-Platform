from __future__ import annotations

from app.orchestrator import QueryOrchestrator


class FakeIntentRouter:
    def __init__(self, intent: str) -> None:
        self.intent = intent

    def classify(self, query: str) -> str:
        return self.intent


class FakeEducationalHandler:
    def __init__(self) -> None:
        self.called = False
        self.last_retrieved_chunks = [{"score": 0.91, "payload": {"text": "Algebra context"}}]
        self.last_context = "[Chunk 1]\nAlgebra context"
        self.last_retrieval_debug = {"deduped_count": 1}

    def handle(self, query: str, conversation_history=None, top_k=None) -> str:
        self.called = True
        return "educational answer"


class FakeConversationalHandler:
    def __init__(self) -> None:
        self.called = False

    def handle(self, query: str, conversation_history=None) -> str:
        self.called = True
        return "conversational answer"


class FakeGreetingHandler:
    def handle(self, query: str) -> str:
        return "hello"


class FakeLLMService:
    last_prompt_messages = [{"role": "user", "content": "preview"}]


class FakeRetriever:
    def close(self) -> None:
        pass


def make_orchestrator(intent: str, educational_handler=None, conversational_handler=None) -> QueryOrchestrator:
    return QueryOrchestrator(
        intent_router=FakeIntentRouter(intent),
        educational_handler=educational_handler or FakeEducationalHandler(),
        conversational_handler=conversational_handler or FakeConversationalHandler(),
        greeting_handler=FakeGreetingHandler(),
        llm_service=FakeLLMService(),
        retriever=FakeRetriever(),
    )


def test_educational_route_uses_educational_handler() -> None:
    educational_handler = FakeEducationalHandler()
    orchestrator = make_orchestrator("educational", educational_handler=educational_handler)

    result = orchestrator.ask("Explain algebra", session_id="test-session", top_k=3)

    assert educational_handler.called is True
    assert result["intent"] == "educational"
    assert result["retrieved_chunks"]
    assert result["context"] == "[Chunk 1]\nAlgebra context"


def test_conversational_route_skips_educational_handler() -> None:
    educational_handler = FakeEducationalHandler()
    conversational_handler = FakeConversationalHandler()
    orchestrator = make_orchestrator(
        "conversational",
        educational_handler=educational_handler,
        conversational_handler=conversational_handler,
    )

    result = orchestrator.ask("Tell me a joke", session_id="test-session")

    assert educational_handler.called is False
    assert conversational_handler.called is True
    assert result["intent"] == "conversational"
    assert result["retrieved_chunks"] == []


def test_greeting_route_returns_greeting_without_retrieval() -> None:
    orchestrator = make_orchestrator("greeting")

    result = orchestrator.ask("Hi", session_id="test-session")

    assert result["intent"] == "greeting"
    assert result["answer"] == "hello"
