from pathlib import Path
import logging
import shutil
import subprocess

from configs.settings import TESSDATA_DIR, TESSERACT_CMD, TESSERACT_CONFIG, TESSERACT_LANGUAGES
from scripts.utils.file_utils import write_text
from scripts.utils.json_utils import save_json
from scripts.utils.path_utils import ensure_dir, page_number_from_name


def ensure_tesseract_available(
    tesseract_cmd: str = TESSERACT_CMD,
    tessdata_dir: Path = TESSDATA_DIR,
    languages: str = TESSERACT_LANGUAGES,
) -> None:
    if not Path(tesseract_cmd).exists() and not shutil.which(tesseract_cmd):
        raise RuntimeError(
            "Tesseract was not found. Install Tesseract OCR or set the correct path "
            "in configs/settings.py."
        )

    if not tessdata_dir.exists():
        raise RuntimeError(f"Tesseract language folder not found: {tessdata_dir}")

    result = subprocess.run(
        [tesseract_cmd, "--tessdata-dir", str(tessdata_dir), "--list-langs"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    installed_languages = set(result.stdout.split())
    requested_languages = set(languages.split("+"))
    missing_languages = requested_languages - installed_languages
    if missing_languages:
        missing = ", ".join(sorted(missing_languages))
        raise RuntimeError(f"Tesseract language packs missing: {missing}")


def extract_text_from_image(
    image_path: Path,
    tesseract_cmd: str = TESSERACT_CMD,
    tessdata_dir: Path = TESSDATA_DIR,
    languages: str = TESSERACT_LANGUAGES,
    config: tuple[str, ...] = TESSERACT_CONFIG,
) -> str:
    command = [
        tesseract_cmd,
        str(image_path),
        "stdout",
        "--tessdata-dir",
        str(tessdata_dir),
        "-l",
        languages,
        *config,
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"Tesseract failed for {image_path}:\n{result.stderr.strip()}")
    return result.stdout.strip()


def extract_ocr_text(
    image_folder: Path,
    text_folder: Path,
    metadata: dict,
    tesseract_cmd: str = TESSERACT_CMD,
    tessdata_dir: Path = TESSDATA_DIR,
    languages: str = TESSERACT_LANGUAGES,
    config: tuple[str, ...] = TESSERACT_CONFIG,
    force: bool = False,
    logger: logging.Logger | None = None,
) -> list[Path]:
    page_folder = ensure_dir(text_folder / "pages")

    images = sorted(image_folder.glob("*.png"), key=page_number_from_name)
    if not images:
        raise FileNotFoundError(f"No page images found in: {image_folder}")

    needs_ocr = force or any(
        not (page_folder / f"page_{page_number_from_name(image_path):03d}.txt").exists()
        for image_path in images
    )
    if needs_ocr:
        ensure_tesseract_available(tesseract_cmd, tessdata_dir, languages)

    combined_pages: list[str] = []
    page_outputs: list[Path] = []

    for image_path in images:
        page_number = page_number_from_name(image_path)
        page_output = page_folder / f"page_{page_number:03d}.txt"

        if page_output.exists() and not force:
            page_text = page_output.read_text(encoding="utf-8").strip()
            if logger:
                logger.info("Reusing OCR page %s", page_output)
        else:
            if logger:
                logger.info("Running OCR for %s", image_path.name)
            page_text = extract_text_from_image(
                image_path=image_path,
                tesseract_cmd=tesseract_cmd,
                tessdata_dir=tessdata_dir,
                languages=languages,
                config=config,
            )
            write_text(page_output, page_text)

        combined_pages.append(f"===== PAGE {page_number} =====\n\n{page_text}")
        page_outputs.append(page_output)

    combined_output = text_folder / "full_text.txt"
    write_text(combined_output, "\n\n".join(combined_pages))

    ocr_metadata = {
        **metadata,
        "language": languages,
        "total_pages": len(images),
        "source_folder": str(image_folder),
        "page_text_folder": str(page_folder),
        "combined_text_file": str(combined_output),
    }
    save_json(ocr_metadata, text_folder / "metadata.json")
    return page_outputs
