import re
from pathlib import Path

CLASS_NAME = "class_10"
SUBJECT_NAME = "algebra"    

OCR_FOLDER = Path("data/ocr_text") / CLASS_NAME / SUBJECT_NAME /"pages"
CLEANED_FOLDER = Path("data/cleaned_text") / CLASS_NAME / SUBJECT_NAME /"pages"

def clean_ocr_text(text: str) -> str:
    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove weird repeated symbols
    text = re.sub(r"[|]{2,}", "|", text)
    
    # Remove excessive repeated dots
    text = re.sub(r"\.{3,}", "...", text)
    
    # Normalize multiple hyphens
    text = re.sub(r"-{2,}", "-", text)

    # Fix broken spacing before punctuation
    text = re.sub(r"\s+([।,:;!?])", r"\1", text)

    # Remove invisible unicode artifacts
    text = text.replace("\ufeff", "")

    # Strip overall text
    text = text.strip()

    return text

def clean_all_pages():

    CLEANED_FOLDER.mkdir(parents=True, exist_ok=True)

    page_files = sorted(OCR_FOLDER.glob("*.txt"))

    if not page_files:
        raise FileNotFoundError(
            f"No OCR text files found in: {OCR_FOLDER}"
        )

    print(f"Reading OCR pages from: {OCR_FOLDER}")
    print(f"Saving cleaned pages to: {CLEANED_FOLDER}")

    for page_file in page_files:

        print(f"Cleaning: {page_file.name}")

        raw_text = page_file.read_text(encoding="utf-8")

        cleaned_text = clean_ocr_text(raw_text)

        output_file = CLEANED_FOLDER / page_file.name

        output_file.write_text(
            cleaned_text,
            encoding="utf-8"
        )

    print("\nText cleaning completed.")


if __name__ == "__main__":
    clean_all_pages()