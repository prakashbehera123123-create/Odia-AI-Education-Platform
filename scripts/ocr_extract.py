from pathlib import Path

import fitz  # PyMuPDF


CLASS_NAME = "class_10"
SUBJECT_NAME = "algebra"
PDF_FILE = Path("data/raw_pdfs") / CLASS_NAME / "10th_Algebra.pdf"
OUTPUT_FOLDER = Path("data/page_images") / CLASS_NAME / SUBJECT_NAME
DPI = 300


def extract_pdf_pages(pdf_file: Path, output_folder: Path, dpi: int = DPI) -> None:
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"Extracting pages from: {pdf_file}")
    print(f"Saving page images to: {output_folder}")

    with fitz.open(pdf_file) as doc:
        for page_index, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=dpi)
            image_path = output_folder / f"{pdf_file.stem}_page_{page_index:03d}.png"
            pix.save(image_path)
            print(f"Saved: {image_path}")

    print("\nPDF page extraction completed.")


if __name__ == "__main__":
    if not PDF_FILE.exists():
        raise FileNotFoundError(f"PDF file not found: {PDF_FILE}")

    extract_pdf_pages(PDF_FILE, OUTPUT_FOLDER)
