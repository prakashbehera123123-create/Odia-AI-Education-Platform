import argparse
from pathlib import Path

from configs.settings import PDF_DPI
from scripts.ingestion.pdf_to_images import extract_pdf_pages
from scripts.utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PDF pages as images.")
    parser.add_argument("pdf_file", type=Path)
    parser.add_argument("output_folder", type=Path)
    parser.add_argument("--dpi", type=int, default=PDF_DPI)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {args.pdf_file}")
    extract_pdf_pages(
        pdf_file=args.pdf_file,
        output_folder=args.output_folder,
        dpi=args.dpi,
        force=args.force,
        logger=get_logger(),
    )


if __name__ == "__main__":
    main()
