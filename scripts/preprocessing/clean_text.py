from pathlib import Path
import logging
import re

from scripts.utils.file_utils import write_text
from scripts.utils.path_utils import ensure_dir


def clean_ocr_text(text: str) -> str:
    # Remove extra spaces, tabs, and newlines, and fix common OCR artifacts
    text = re.sub(r"[ \t]+", " ", text)
    # Replace multiple newlines with a single newline, but keep paragraph breaks
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    # Fix common OCR artifacts like multiple pipes, ellipses, and dashes
    text = re.sub(r"[|]{2,}", "|", text)
    # Replace multiple dots with a single ellipsis
    text = re.sub(r"\.{3,}", "...", text)
    # Replace multiple dashes with a single dash
    text = re.sub(r"-{2,}", "-", text)
    # Remove spaces before punctuation (e.g., "word ." -> "word.")
    text = re.sub(r"\s+([।,:;!?])", r"\1", text)
    # Remove control characters while preserving Unicode text such as Odia.
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    text = text.replace("\ufeff", "")
    return text.strip()


# Clean OCR text files in a folder and save cleaned versions to another folder

def clean_pages(
    ocr_pages_folder: Path,
    cleaned_pages_folder: Path,
    force: bool = False,
    logger: logging.Logger | None = None,
) -> list[Path]:
    ensure_dir(cleaned_pages_folder)
    page_files = sorted(ocr_pages_folder.glob("*.txt"))
    if not page_files:
        raise FileNotFoundError(f"No OCR text files found in: {ocr_pages_folder}")

    cleaned_files: list[Path] = []
    for page_file in page_files:
        output_file = cleaned_pages_folder / page_file.name
        if output_file.exists() and not force:
            if logger:
                logger.info("Reusing cleaned page %s", output_file)
            cleaned_files.append(output_file)
            continue

        cleaned_text = clean_ocr_text(page_file.read_text(encoding="utf-8"))
        write_text(output_file, cleaned_text)
        cleaned_files.append(output_file)

    return cleaned_files
