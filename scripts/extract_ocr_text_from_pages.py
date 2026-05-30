import argparse
from pathlib import Path

from scripts.ingestion.run_ocr import (
    ensure_tesseract_available,
    extract_ocr_text,
    extract_text_from_image,
)
from scripts.utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Tesseract OCR over page images.")
    parser.add_argument("image_folder", type=Path)
    parser.add_argument("text_folder", type=Path)
    parser.add_argument("--class-name", default="unknown_class")
    parser.add_argument("--subject", default="unknown_subject")
    parser.add_argument("--book", default="unknown_book")
    parser.add_argument("--source-file", default="")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extract_ocr_text(
        image_folder=args.image_folder,
        text_folder=args.text_folder,
        metadata={
            "class": args.class_name,
            "subject": args.subject,
            "book": args.book,
            "chapter": None,
            "source_file": args.source_file,
        },
        force=args.force,
        logger=get_logger(),
    )


if __name__ == "__main__":
    main()
