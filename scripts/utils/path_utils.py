import re
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

# Note: The slugify and infer_subject_from_pdf_stem functions are currently not used in the codebase, but they can be helpful for future extensions where we might want to infer subject names from PDF file names or create slugs for folder names.
def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"

# This function can be used to infer subject names from PDF file names, which can be helpful for organizing the extracted data. For example, a PDF named "Class_10_Mathematics.pdf" would yield a subject name of "mathematics".
def infer_subject_from_pdf_stem(stem: str) -> str:
    cleaned = re.sub(r"^\d+(st|nd|rd|th)?[_\-\s]*", "", stem, flags=re.IGNORECASE)
    return slugify(cleaned)

# The page_number_from_name and sorted_page_files functions are used to sort the extracted page files in the correct order based on their page numbers, which is crucial for maintaining the logical flow of the content when processing the OCR text later on.
def page_number_from_name(path: Path) -> int:
    match = re.search(r"(?:page|PAGE)[_\-\s]*(\d+)", path.stem)
    return int(match.group(1)) if match else 0

# The sorted_page_files function retrieves all text files in a given folder and sorts them based on their page numbers extracted from the file names, ensuring that the pages are processed in the correct sequence.
def sorted_page_files(folder: Path, pattern: str = "*.txt") -> list[Path]:
    return sorted(folder.glob(pattern), key=page_number_from_name)
