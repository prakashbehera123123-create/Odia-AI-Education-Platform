from dataclasses import dataclass
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"

RAW_PDF_ROOT = DATA_ROOT / "raw_pdfs"
PAGE_IMAGE_ROOT = DATA_ROOT / "page_images"
OCR_TEXT_ROOT = DATA_ROOT / "ocr_text"
CLEANED_TEXT_ROOT = DATA_ROOT / "cleaned_text"
CHUNK_ROOT = DATA_ROOT / "chunks"
META_DATA_ROOT = DATA_ROOT / "meta_data"
TESSDATA_DIR = DATA_ROOT / "tessdata"
QDRANT_DB_PATH = DATA_ROOT / "qdrant_db"

DEFAULT_WINDOWS_TESSERACT_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSERACT_CMD = (
    str(DEFAULT_WINDOWS_TESSERACT_PATH)
    if DEFAULT_WINDOWS_TESSERACT_PATH.exists()
    else shutil.which("tesseract") or "tesseract"
)

TESSERACT_LANGUAGES = "ori+eng"
TESSERACT_CONFIG = ("--psm", "6", "--oem", "1", "-c", "preserve_interword_spaces=1")

PDF_DPI = 300
MAX_CHUNK_SIZE = 700
OVERLAP_SIZE = 120
DEFAULT_MAX_WORKERS = 2

EMBEDDING_MODEL = "BAAI/bge-m3"
VECTOR_DIMENSION = 1024
COLLECTION_NAME = "odia_education_chunks"
EMBEDDING_BATCH_SIZE = 16


@dataclass(frozen=True)
class PipelineSettings:
    raw_pdf_root: Path = RAW_PDF_ROOT
    page_image_root: Path = PAGE_IMAGE_ROOT
    ocr_text_root: Path = OCR_TEXT_ROOT
    cleaned_text_root: Path = CLEANED_TEXT_ROOT
    chunk_root: Path = CHUNK_ROOT
    meta_data_root: Path = META_DATA_ROOT
    tessdata_dir: Path = TESSDATA_DIR
    tesseract_cmd: str = TESSERACT_CMD
    tesseract_languages: str = TESSERACT_LANGUAGES
    tesseract_config: tuple[str, ...] = TESSERACT_CONFIG
    pdf_dpi: int = PDF_DPI
    max_chunk_size: int = MAX_CHUNK_SIZE
    overlap_size: int = OVERLAP_SIZE
    max_workers: int = DEFAULT_MAX_WORKERS
    force: bool = False


@dataclass(frozen=True)
class EmbeddingSettings:
    chunk_root: Path = CHUNK_ROOT
    qdrant_db_path: Path = QDRANT_DB_PATH
    embedding_model: str = EMBEDDING_MODEL
    vector_dimension: int = VECTOR_DIMENSION
    collection_name: str = COLLECTION_NAME
    embedding_batch_size: int = EMBEDDING_BATCH_SIZE
