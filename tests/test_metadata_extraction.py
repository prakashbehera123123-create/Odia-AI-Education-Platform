from scripts.ingestion.metadata_extraction import PageMetadataState, build_page_object
from scripts.preprocessing.clean_text import clean_ocr_text


def test_build_page_object_extracts_and_inherits_metadata() -> None:
    first_page, state = build_page_object(
        text="Chapter 7: Russian Revolution\n\n1 Causes\n1.1 Political Causes\nText",
        page_number=42,
        base_metadata={
            "class": "class_10",
            "board": "BSE Odisha",
            "subject": "history",
            "language": "odia",
            "source_pdf": "History.pdf",
        },
    )

    second_page, _ = build_page_object(
        text="Continuation paragraph only.",
        page_number=43,
        base_metadata={
            "class": "class_10",
            "board": "BSE Odisha",
            "subject": "history",
            "language": "odia",
            "source_pdf": "History.pdf",
        },
        previous_state=state,
    )

    assert first_page["page_number"] == 42
    assert first_page["chapter_number"] == 7
    assert first_page["chapter_name"] == "Russian Revolution"
    assert first_page["section"] == "Causes"
    assert first_page["subsection"] == "Political Causes"
    assert second_page["chapter_number"] == 7
    assert second_page["chapter_name"] == "Russian Revolution"


def test_build_page_object_uses_previous_state_when_chapter_missing() -> None:
    previous_state = PageMetadataState(chapter_number=3, chapter_name="Previous", section="Section")

    page, state = build_page_object(
        text="Plain page text",
        page_number=5,
        base_metadata={"class": "class_10", "subject": "history", "source_pdf": "book.pdf"},
        previous_state=previous_state,
        ocr_languages="ori+eng",
    )

    assert page["language"] == "odia"
    assert page["board"] is None
    assert page["chapter_number"] == 3
    assert page["chapter_name"] == "Previous"
    assert state.section == "Section"


def test_clean_ocr_text_preserves_odia_unicode() -> None:
    assert clean_ocr_text("ଓଡ଼ିଆ   ପାଠ\n\n\nChapter") == "ଓଡ଼ିଆ ପାଠ\n\nChapter"
