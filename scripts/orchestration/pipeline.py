from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
import traceback

from configs.settings import PipelineSettings
from scripts.ingestion.pdf_to_images import extract_pdf_pages
from scripts.ingestion.run_ocr import extract_ocr_text
from scripts.preprocessing.clean_text import clean_pages
from scripts.preprocessing.chunk_text import chunk_cleaned_pages
from scripts.utils.file_utils import list_pdfs
from scripts.utils.json_utils import save_json
from scripts.utils.logger import get_logger
from scripts.utils.path_utils import ensure_dir, infer_subject_from_pdf_stem, slugify


@dataclass(frozen=True)
class PdfJob:
    pdf_path: Path
    class_name: str
    subject: str
    book: str
    use_book_folder: bool


@dataclass(frozen=True)
class PipelineResult:
    pdf_path: str
    status: str
    class_name: str
    subject: str
    book: str
    chunks_file: str | None = None
    error: str | None = None


def discover_pdf_jobs(settings: PipelineSettings) -> list[PdfJob]:
    jobs: list[PdfJob] = []
    for pdf_path in list_pdfs(settings.raw_pdf_root):
        relative_path = pdf_path.relative_to(settings.raw_pdf_root)
        parts = relative_path.parts
        class_name = parts[0] if len(parts) > 1 else "unknown_class"

        if len(parts) >= 3:
            subject = slugify(parts[-2])
        else:
            subject = infer_subject_from_pdf_stem(pdf_path.stem)

        jobs.append(
            PdfJob(
                pdf_path=pdf_path,
                class_name=slugify(class_name),
                subject=subject,
                book=slugify(pdf_path.stem),
                use_book_folder=len(parts) >= 3,
            )
        )
    return jobs


def build_metadata(job: PdfJob) -> dict:
    return {
        "class": job.class_name,
        "subject": job.subject,
        "book": job.book,
        "chapter": None,
        "source_file": str(job.pdf_path),
    }


def output_base(root: Path, job: PdfJob) -> Path:
    base = root / job.class_name / job.subject
    return base / job.book if job.use_book_folder else base


def process_pdf(job: PdfJob, settings: PipelineSettings) -> PipelineResult:
    logger = get_logger()
    metadata = build_metadata(job)

    image_folder = output_base(settings.page_image_root, job)
    ocr_folder = output_base(settings.ocr_text_root, job)
    cleaned_folder = output_base(settings.cleaned_text_root, job)
    chunk_folder = ensure_dir(output_base(settings.chunk_root, job))
    chunks_file = chunk_folder / "chunks.json"

    try:
        logger.info("Starting pipeline for %s", job.pdf_path)
        extract_pdf_pages(
            pdf_file=job.pdf_path,
            output_folder=image_folder,
            dpi=settings.pdf_dpi,
            force=settings.force,
            logger=logger,
        )
        extract_ocr_text(
            image_folder=image_folder,
            text_folder=ocr_folder,
            metadata=metadata,
            tesseract_cmd=settings.tesseract_cmd,
            tessdata_dir=settings.tessdata_dir,
            languages=settings.tesseract_languages,
            config=settings.tesseract_config,
            force=settings.force,
            logger=logger,
        )
        clean_pages(
            ocr_pages_folder=ocr_folder / "pages",
            cleaned_pages_folder=cleaned_folder / "pages",
            force=settings.force,
            logger=logger,
        )
        chunk_cleaned_pages(
            cleaned_pages_folder=cleaned_folder / "pages",
            output_file=chunks_file,
            metadata=metadata,
            max_chunk_size=settings.max_chunk_size,
            overlap_size=settings.overlap_size,
            force=settings.force,
            logger=logger,
        )

        logger.info("Completed pipeline for %s", job.pdf_path)
        return PipelineResult(
            pdf_path=str(job.pdf_path),
            status="success",
            class_name=job.class_name,
            subject=job.subject,
            book=job.book,
            chunks_file=str(chunks_file),
        )
    except Exception as exc:
        logger.error("Pipeline failed for %s: %s", job.pdf_path, exc)
        return PipelineResult(
            pdf_path=str(job.pdf_path),
            status="failed",
            class_name=job.class_name,
            subject=job.subject,
            book=job.book,
            chunks_file=str(chunks_file),
            error=f"{exc}\n{traceback.format_exc()}",
        )


def process_all(settings: PipelineSettings | None = None, parallel: bool = False) -> list[PipelineResult]:
    settings = settings or PipelineSettings()
    logger = get_logger(log_file=settings.meta_data_root / "pipeline.log")
    jobs = discover_pdf_jobs(settings)
    if not jobs:
        raise FileNotFoundError(f"No PDFs found under: {settings.raw_pdf_root}")

    logger.info("Discovered %s PDF files", len(jobs))

    if not parallel or settings.max_workers <= 1:
        results = [process_pdf(job, settings) for job in jobs]
    else:
        results = []
        with ProcessPoolExecutor(max_workers=settings.max_workers) as executor:
            future_to_job = {executor.submit(process_pdf, job, settings): job for job in jobs}
            for future in as_completed(future_to_job):
                results.append(future.result())

    summary_file = settings.meta_data_root / "pipeline_summary.json"
    save_json([asdict(result) for result in results], summary_file)
    logger.info("Saved pipeline summary to %s", summary_file)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Odia AI ingestion pipeline.")
    parser.add_argument("--parallel", action="store_true", help="Process PDFs with multiprocessing.")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes.")
    parser.add_argument("--force", action="store_true", help="Rebuild outputs even when files exist.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_settings = PipelineSettings()
    settings = PipelineSettings(
        **{
            **asdict(base_settings),
            "max_workers": args.workers or base_settings.max_workers,
            "force": args.force,
        }
    )
    process_all(settings=settings, parallel=args.parallel)


if __name__ == "__main__":
    main()
