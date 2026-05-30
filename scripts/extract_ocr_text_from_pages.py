import re
import shutil
import subprocess
from pathlib import Path
import json


CLASS_NAME = "class_10"
SUBJECT_NAME = "algebra"
IMAGE_FOLDER = Path("data/page_images") / CLASS_NAME / SUBJECT_NAME
TEXT_FOLDER = Path("data/ocr_text") / CLASS_NAME / SUBJECT_NAME
WINDOWS_TESSERACT_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSERACT_CMD = str(WINDOWS_TESSERACT_PATH) if WINDOWS_TESSERACT_PATH.exists() else "tesseract"
TESSDATA_DIR = Path("data/tessdata")
TESSERACT_LANGUAGES = "ori+eng"
TESSERACT_CONFIG = ["--psm", "6", "--oem", "1", "-c", "preserve_interword_spaces=1"]


def page_number_from_name(image_path: Path) -> int:
    match = re.search(r"_page_(\d+)", image_path.stem)
    return int(match.group(1)) if match else 0


def ensure_tesseract_available() -> None:
    if not Path(TESSERACT_CMD).exists() and not shutil.which(TESSERACT_CMD):
        raise RuntimeError(
            "Tesseract was not found. Install Tesseract OCR, or update "
            "WINDOWS_TESSERACT_PATH in this script to the correct tesseract.exe path."
        )

    if not TESSDATA_DIR.exists():
        raise RuntimeError(f"Tesseract language folder not found: {TESSDATA_DIR}")

    result = subprocess.run(
        [TESSERACT_CMD, "--tessdata-dir", str(TESSDATA_DIR), "--list-langs"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    installed_languages = set(result.stdout.split())
    missing_languages = {"ori", "eng"} - installed_languages

    if missing_languages:
        missing = ", ".join(sorted(missing_languages))
        raise RuntimeError(
            f"Tesseract is installed, but these language packs are missing: {missing}. "
            "Install Odia (`ori`) and English (`eng`) traineddata files before running OCR."
        )


def extract_text_from_image(image_path: Path) -> str:
    command = [
        TESSERACT_CMD,
        str(image_path),
        "stdout",
        "--tessdata-dir",
        str(TESSDATA_DIR),
        "-l",
        TESSERACT_LANGUAGES,
        *TESSERACT_CONFIG,
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        raise RuntimeError(
            f"Tesseract failed for {image_path}:\n{result.stderr.strip()}"
        )

    return result.stdout.strip()


def extract_ocr_text(image_folder: Path, text_folder: Path) -> None:
    ensure_tesseract_available()

    page_folder = text_folder / "pages"
    page_folder.mkdir(parents=True, exist_ok=True)

    images = sorted(image_folder.glob("*.png"), key=page_number_from_name)
    if not images:
        raise FileNotFoundError(f"No page images found in: {image_folder}")

    combined_pages = []

    print(f"Reading page images from: {image_folder}")
    print(f"Saving OCR text to: {text_folder}")
    print(f"Using Tesseract languages: {TESSERACT_LANGUAGES}")

    for image_path in images:
        page_number = page_number_from_name(image_path)
        page_output = page_folder / f"page_{page_number:03d}.txt"

        if page_output.exists():
            print(f"Reusing existing OCR text for page {page_number}: {page_output.name}")
            page_text = page_output.read_text(encoding="utf-8").strip()
        else:
            print(f"Extracting OCR text from page {page_number}: {image_path.name}")
            page_text = extract_text_from_image(image_path)
            page_output.write_text(page_text, encoding="utf-8")

        combined_pages.append(f"===== PAGE {page_number} =====\n\n{page_text}")

    combined_output = text_folder / "full_text.txt"
    combined_output.write_text("\n\n".join(combined_pages), encoding="utf-8")

    metadata = {
        "class": CLASS_NAME,
        "subject": SUBJECT_NAME,
        "language": TESSERACT_LANGUAGES,
        "total_pages": len(images),
        "source_folder": str(image_folder),
        "page_text_folder": str(page_folder),
        "combined_text_file": str(combined_output),
    }
    metadata_file = text_folder / "metadata.json"
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved combined OCR text: {combined_output}")
    print(f"Saved metadata: {metadata_file}")
    print("OCR text extraction completed.")


if __name__ == "__main__":
    extract_ocr_text(IMAGE_FOLDER, TEXT_FOLDER)
