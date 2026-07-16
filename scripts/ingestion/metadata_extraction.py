from __future__ import annotations

from dataclasses import dataclass, replace
import logging
import re
from pathlib import Path
from typing import Any


ODIA_DIGITS = str.maketrans("୦୧୨୩୪୫୬୭୮୯", "0123456789")
CHAPTER_KEYWORDS = ("chapter", "ଅଧ୍ୟାୟ", "ପାଠ")
SECTION_KEYWORDS = (
    "exercise",
    "exercises",
    "summary",
    "questions",
    "activities",
    "activity",
    "ଅଭ୍ୟାସ",
    "ସାରାଂଶ",
    "ପ୍ରଶ୍ନ",
)


@dataclass(frozen=True)
class PageMetadataState:
    chapter_number: int | str | None = None
    chapter_name: str | None = None
    section: str | None = None
    subsection: str | None = None


def normalize_language(languages: str | None) -> str:
    if not languages:
        return "unknown"

    language_codes = {language.strip().lower() for language in languages.split("+")}
    if "ori" in language_codes or "or" in language_codes:
        return "odia"
    if "eng" in language_codes:
        return "english"
    return "+".join(sorted(language_codes)) or "unknown"


def normalize_chapter_number(value: str | None) -> int | str | None:
    if not value:
        return None

    normalized = value.strip().translate(ODIA_DIGITS)
    if normalized.isdigit():
        return int(normalized)
    return normalized


def extract_chapter(text: str) -> tuple[int | str | None, str | None]:
    lines = iter_clean_lines(text)
    for line in lines:
        lower_line = line.lower()
        if not any(keyword in lower_line for keyword in CHAPTER_KEYWORDS):
            continue

        match = re.search(
            r"(?:chapter|ଅଧ୍ୟାୟ|ପାଠ)\s*[-:।.]?\s*([0-9୦-୯ivxlcdmIVXLCDM]+)?\s*[-:।.]?\s*(.*)",
            line,
            flags=re.IGNORECASE,
        )
        if not match:
            continue

        chapter_number = normalize_chapter_number(match.group(1))
        chapter_name = clean_heading(match.group(2))
        return chapter_number, chapter_name

    return None, None


def extract_section_hierarchy(text: str, chapter_name: str | None = None) -> tuple[str | None, str | None]:
    section: str | None = None
    subsection: str | None = None

    for line in iter_clean_lines(text):
        if chapter_name and line.strip() == chapter_name:
            continue

        numeric_match = re.match(r"^([0-9୦-୯]+(?:\.[0-9୦-୯]+)*)\s+(.{3,100})$", line)
        if numeric_match:
            level = numeric_match.group(1).count(".")
            heading = clean_heading(numeric_match.group(2))
            if not heading:
                continue
            if level == 0 and section is None:
                section = heading
            elif level > 0 and subsection is None:
                subsection = heading
            if section and subsection:
                return section, subsection
            continue

        if is_keyword_heading(line) and section is None:
            section = clean_heading(line)
            continue

        if section and subsection is None and looks_like_heading(line):
            subsection = clean_heading(line)
            return section, subsection

    return section, subsection


def build_page_object(
    text: str,
    page_number: int,
    base_metadata: dict[str, Any],
    previous_state: PageMetadataState | None = None,
    ocr_languages: str | None = None,
    logger: logging.Logger | None = None,
) -> tuple[dict[str, Any], PageMetadataState]:
    previous_state = previous_state or PageMetadataState()
    chapter_number, chapter_name = extract_chapter(text)
    if chapter_number is None:
        chapter_number = previous_state.chapter_number
    if chapter_name is None:
        chapter_name = previous_state.chapter_name

    section, subsection = extract_section_hierarchy(text, chapter_name)
    if section is None:
        section = previous_state.section
    if subsection is None:
        subsection = previous_state.subsection

    state = replace(
        previous_state,
        chapter_number=chapter_number,
        chapter_name=chapter_name,
        section=section,
        subsection=subsection,
    )
    source_pdf = str(base_metadata.get("source_pdf") or base_metadata.get("source_file") or "")
    page_object = {
        "text": text,
        "clean_text": text,
        "page_number": page_number,
        "page": page_number,
        "class": base_metadata.get("class"),
        "board": base_metadata.get("board"),
        "subject": base_metadata.get("subject"),
        "language": base_metadata.get("language") or normalize_language(ocr_languages),
        "chapter_number": state.chapter_number,
        "chapter_name": state.chapter_name,
        "section": state.section,
        "subsection": state.subsection,
        "source_pdf": source_pdf,
        "source": Path(source_pdf).name if source_pdf else "",
    }
    log_missing_metadata(page_object, logger)
    return page_object, state


def log_missing_metadata(
    page_object: dict[str, Any],
    logger: logging.Logger | None = None,
) -> None:
    required_fields = (
        "text",
        "page_number",
        "class",
        "board",
        "subject",
        "language",
        "chapter_number",
        "chapter_name",
        "section",
        "subsection",
        "source_pdf",
    )
    missing = [
        field_name
        for field_name in required_fields
        for value in [page_object.get(field_name)]
        if value is None or value == ""
    ]
    if missing and logger:
        logger.warning(
            "Metadata extraction incomplete for page %s | missing=%s",
            page_object.get("page_number"),
            ",".join(missing),
        )


def iter_clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def clean_heading(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip(" -:।.\t")
    return cleaned or None


def is_keyword_heading(line: str) -> bool:
    cleaned = clean_heading(line)
    if not cleaned:
        return False
    return cleaned.lower() in SECTION_KEYWORDS


def looks_like_heading(line: str) -> bool:
    cleaned = clean_heading(line)
    if not cleaned or len(cleaned) > 100:
        return False
    if cleaned.endswith((".", ",", ";", ":")):
        return False
    word_count = len(cleaned.split())
    return 1 <= word_count <= 8
