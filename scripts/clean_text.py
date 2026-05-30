import argparse
from pathlib import Path

from scripts.preprocessing.clean_text import clean_ocr_text, clean_pages
from scripts.utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean OCR page text files.")
    parser.add_argument("ocr_pages_folder", type=Path)
    parser.add_argument("cleaned_pages_folder", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    clean_pages(
        ocr_pages_folder=args.ocr_pages_folder,
        cleaned_pages_folder=args.cleaned_pages_folder,
        force=args.force,
        logger=get_logger(),
    )


if __name__ == "__main__":
    main()
