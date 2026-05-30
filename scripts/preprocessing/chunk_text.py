from pathlib import Path
import logging
import re

from configs.settings import MAX_CHUNK_SIZE, OVERLAP_SIZE
from scripts.utils.json_utils import save_json
from scripts.utils.path_utils import page_number_from_name


def split_semantic_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def build_hybrid_chunks(
    paragraphs: list[str],
    max_chunk_size: int = MAX_CHUNK_SIZE,
    overlap_size: int = OVERLAP_SIZE,
) -> list[str]:
    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 1 <= max_chunk_size:
            current_chunk += ("\n" if current_chunk else "") + paragraph
            continue

        if current_chunk:
            chunks.append(current_chunk)

        if len(paragraph) > max_chunk_size:
            start = 0
            while start < len(paragraph):
                end = start + max_chunk_size
                chunks.append(paragraph[start:end])
                next_start = end - overlap_size
                start = next_start if next_start > start else end
            current_chunk = ""
        else:
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def chunk_cleaned_pages(
    cleaned_pages_folder: Path,
    output_file: Path,
    metadata: dict,
    max_chunk_size: int = MAX_CHUNK_SIZE,
    overlap_size: int = OVERLAP_SIZE,
    force: bool = False,
    logger: logging.Logger | None = None,
) -> list[dict]:
    if output_file.exists() and not force:
        if logger:
            logger.info("Reusing chunks file %s", output_file)
        return []

    page_files = sorted(cleaned_pages_folder.glob("*.txt"), key=page_number_from_name)
    if not page_files:
        raise FileNotFoundError(f"No cleaned text files found in: {cleaned_pages_folder}")

    all_chunks: list[dict] = []
    chunk_id = 1
    for page_file in page_files:
        page_number = page_number_from_name(page_file)
        text = page_file.read_text(encoding="utf-8")
        paragraphs = split_semantic_paragraphs(text)
        chunks = build_hybrid_chunks(paragraphs, max_chunk_size, overlap_size)

        for chunk_index, chunk in enumerate(chunks, start=1):
            all_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "class": metadata["class"],
                    "subject": metadata["subject"],
                    "book": metadata["book"],
                    "chapter": metadata.get("chapter"),
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "source_file": metadata["source_file"],
                    "text": chunk,
                }
            )
            chunk_id += 1

    save_json(all_chunks, output_file)
    if logger:
        logger.info("Saved %s chunks to %s", len(all_chunks), output_file)
    return all_chunks
