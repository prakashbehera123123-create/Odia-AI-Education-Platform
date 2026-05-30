from pathlib import Path

from configs.settings import CLEANED_TEXT_ROOT, CHUNK_ROOT, MAX_CHUNK_SIZE, OVERLAP_SIZE
from scripts.preprocessing.chunk_text import build_hybrid_chunks, chunk_cleaned_pages, split_semantic_paragraphs


CLEAN_ROOT = CLEANED_TEXT_ROOT

#

def split_simentic_paragraphs(text: str) -> list[str]:
    return split_semantic_paragraphs(text)


def process_subject(subject_folder: Path) -> None:
    relative_path = subject_folder.relative_to(CLEAN_ROOT)
    if len(relative_path.parts) < 2:
        raise ValueError(
            "Expected cleaned text folders to follow class/subject/pages or class/subject/book/pages. "
            f"Got: {subject_folder}"
        )

    class_name, subject_name = relative_path.parts[:2]
    book_name = relative_path.parts[2] if len(relative_path.parts) >= 3 else subject_name
    output_folder = CHUNK_ROOT / class_name / subject_name
    if len(relative_path.parts) >= 3:
        output_folder = output_folder / book_name
    output_file = output_folder / "chunks.json"
    metadata = {
        "class": class_name,
        "subject": subject_name,
        "book": book_name,
        "chapter": None,
        "source_file": "",
    }
    chunk_cleaned_pages(
        cleaned_pages_folder=subject_folder / "pages",
        output_file=output_file,
        metadata=metadata,
        max_chunk_size=MAX_CHUNK_SIZE,
        overlap_size=OVERLAP_SIZE,
        force=True,
    )

def main():
    subject_folders = [
        folder
        for folder in CLEAN_ROOT.rglob("*")
        if (folder / "pages").exists()
    ]

    for subject_folder in subject_folders:
        process_subject(subject_folder)


if __name__ == "__main__":
    main()
