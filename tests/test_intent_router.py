from __future__ import annotations

from app.intent import IntentRouter


def test_classifier_returns_valid_educational_label() -> None:
    router = IntentRouter(classifier=lambda query: "educational")

    assert router.classify("Explain Algebra") == "educational"


def test_classifier_normalizes_markdown_noise() -> None:
    router = IntentRouter(classifier=lambda query: "`greeting`")

    assert router.classify("Hi") == "greeting"


def test_invalid_classifier_output_falls_back_to_out_of_scope() -> None:
    router = IntentRouter(classifier=lambda query: '{"intent": "educational"}')

    assert router.classify("Explain Algebra") == "out_of_scope"


def test_empty_query_is_out_of_scope_without_llm_call() -> None:
    called = False

    def classifier(query: str) -> str:
        nonlocal called
        called = True
        return "educational"

    router = IntentRouter(classifier=classifier)

    assert router.classify("   ") == "out_of_scope"
    assert called is False
