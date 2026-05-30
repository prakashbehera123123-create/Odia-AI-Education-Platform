


# This script extracts text from PDFs using PyMuPDF (fitz) and saves it as .txt files(not required now since we are doing OCR on page images, but keeping it here for reference). It processes all PDFs in the specified input folder and saves the extracted text in the output folder.)
# import fitz  # PyMuPDF
# from pathlib import Path

# # Input and output folders
# PDF_FOLDER = Path("data/raw_pdfs/class_10")
# OUTPUT_FOLDER = Path("data/extracted_text")

# # Create output folder if not exists
# OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# # Loop through all PDFs
# for pdf_file in PDF_FOLDER.glob("*.pdf"):

#     print(f"\nProcessing: {pdf_file.name}")

#     # Open PDF
#     doc = fitz.open(pdf_file)

#     full_text = []

#     # Extract page-wise text
#     for page_num, page in enumerate(doc):

#         text = page.get_text()

#         full_text.append(
#             f"\n\n===== PAGE {page_num + 1} =====\n\n{text}"
#         )

#     # Save extracted text
#     output_file = OUTPUT_FOLDER / f"{pdf_file.stem}.txt"

#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write("".join(full_text))

#     print(f"Saved: {output_file}")

# print("\nText extraction completed.")
