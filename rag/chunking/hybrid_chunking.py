import json
import re
from pathlib import Path

CLEAN_ROOT = Path("data/cleaned_text") 
CHUNK_ROOT = Path("data/chunks")

MAX_CHUNK_SIZE = 700
OVERLAP_SIZE = 120

def split_simentic_paragraphs(text: str) -> list[str]:
    # Split by double newlines to get paragraphs
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]

def build_hybrid_chunks(paragraphs: list[str], max_chunk_size: int = MAX_CHUNK_SIZE, overlap_size: int = OVERLAP_SIZE) -> list[str]:
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 1 <= max_chunk_size:
            current_chunk += ("\n" if current_chunk else "") + paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Start new chunk with overlap
            current_chunk = paragraph[-overlap_size:] if overlap_size < len(paragraph) else paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def process_subject(subject_folder):

    relative_path = subject_folder.relative_to(CLEAN_ROOT)

    class_name = relative_path.parts[0]
    subject_name = relative_path.parts[1]

    output_folder = CHUNK_ROOT / class_name / subject_name

    output_folder.mkdir(parents=True, exist_ok=True)

    all_chunks = []

    chunk_id = 1

    page_files = sorted(subject_folder.glob("pages/*.txt"))

    for page_file in page_files:

        print(f"Chunking: {page_file}")

        text = page_file.read_text(
            encoding="utf-8"
        )

        paragraphs = split_simentic_paragraphs(text)

        chunks = build_hybrid_chunks(paragraphs)

        for idx, chunk in enumerate(chunks, start=1):

            chunk_data = {
                "chunk_id": chunk_id,
                "class": class_name,
                "subject": subject_name,
                "page": page_file.stem,
                "chunk_index": idx,
                "text": chunk,
            }

            all_chunks.append(chunk_data)

            chunk_id += 1

    output_file = output_folder / "chunks.json"

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(
            all_chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"\nSaved chunks: {output_file}")


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