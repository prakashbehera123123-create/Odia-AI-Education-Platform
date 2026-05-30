from pathlib import Path
import logging

import fitz

from configs.settings import PDF_DPI
from scripts.utils.path_utils import ensure_dir


def extract_pdf_pages(
    pdf_file: Path,
    output_folder: Path,
    dpi: int = PDF_DPI,
    force: bool = False,
    logger: logging.Logger | None = None,
) -> list[Path]:
    ensure_dir(output_folder)
    existing_pages = sorted(output_folder.glob(f"{pdf_file.stem}_page_*.png"))
    if existing_pages and not force:
        if logger:
            logger.info("Reusing %s existing page images for %s", len(existing_pages), pdf_file.name)
        return existing_pages

    saved_pages: list[Path] = []
    if logger:
        logger.info("Extracting page images from %s", pdf_file)

    with fitz.open(pdf_file) as doc:
        for page_index, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=dpi)
            image_path = output_folder / f"{pdf_file.stem}_page_{page_index:03d}.png"
            pix.save(image_path)
            saved_pages.append(image_path)

    if logger:
        logger.info("Saved %s page images to %s", len(saved_pages), output_folder)
    return saved_pages
