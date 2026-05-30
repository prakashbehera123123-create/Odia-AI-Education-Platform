from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
import uuid

from configs.settings import EmbeddingSettings
from rag.embeddings.embedder import Embedder
from rag.vectordb.qdrant_store import QdrantStore
from scripts.utils.json_utils import load_json
from scripts.utils.logger import get_logger


PAYLOAD_FIELDS = (
    "class",
    "subject",
    "book",
    "chapter",
    "page",
    "chunk_index",
    "source_file",
    "text",
)


def discover_chunk_files(chunk_root: Path) -> list[Path]:
    return sorted(chunk_root.rglob("chunks.json"))


def make_point_id(source_file: str, chunk_id: int | str) -> str:
    stable_key = f"{source_file}:{chunk_id}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, stable_key))


def normalize_payload(chunk: dict[str, Any], chunk_file: Path) -> dict[str, Any]:
    source_file = str(chunk.get("source_file") or chunk_file)
    payload = {
        "class": chunk.get("class"),
        "subject": chunk.get("subject"),
        "book": chunk.get("book") or chunk.get("subject"),
        "chapter": chunk.get("chapter"),
        "page": chunk.get("page"),
        "chunk_index": chunk.get("chunk_index"),
        "source_file": source_file,
        "text": chunk.get("text", ""),
    }
    return {field: payload.get(field) for field in PAYLOAD_FIELDS}


def iter_batches(items: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    return [items[start : start + batch_size] for start in range(0, len(items), batch_size)]


def load_chunks_from_file(chunk_file: Path) -> list[dict[str, Any]]:
    chunks = load_json(chunk_file)
    if not isinstance(chunks, list):
        raise ValueError(f"Expected a list of chunks in {chunk_file}")
    return [chunk for chunk in chunks if isinstance(chunk, dict) and chunk.get("text")]


def embed_all_chunks(settings: EmbeddingSettings | None = None) -> None:
    settings = settings or EmbeddingSettings()
    logger = get_logger("odia_ai_embeddings")

    chunk_files = discover_chunk_files(settings.chunk_root)
    if not chunk_files:
        raise FileNotFoundError(f"No chunks.json files found under: {settings.chunk_root}")

    logger.info("Discovered %s chunk files", len(chunk_files))
    embedder = Embedder(settings.embedding_model)
    store = QdrantStore(
        db_path=settings.qdrant_db_path,
        collection_name=settings.collection_name,
        vector_dimension=settings.vector_dimension,
    )
    try:
        store.initialize_collection()

        total_uploaded = 0
        for chunk_file in chunk_files:
            chunks = load_chunks_from_file(chunk_file)
            logger.info("Embedding %s chunks from %s", len(chunks), chunk_file)

            for batch in iter_batches(chunks, settings.embedding_batch_size):
                texts = [chunk["text"] for chunk in batch]
                vectors = embedder.embed_batch(texts, batch_size=settings.embedding_batch_size)

                ids: list[str] = []
                payloads: list[dict[str, Any]] = []
                for chunk in batch:
                    payload = normalize_payload(chunk, chunk_file)
                    chunk_id = chunk.get("chunk_id")
                    if chunk_id is None:
                        chunk_id = f"{payload.get('page')}:{payload.get('chunk_index')}"
                    ids.append(make_point_id(payload["source_file"], chunk_id))
                    payloads.append(payload)

                store.upload_vectors(ids=ids, vectors=vectors, payloads=payloads)
                total_uploaded += len(batch)
                logger.info("Uploaded %s vectors so far", total_uploaded)

        logger.info("Embedding pipeline completed. Uploaded %s vectors.", total_uploaded)
    finally:
        store.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed chunks and upload them to Qdrant.")
    parser.add_argument("--chunk-root", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_settings = EmbeddingSettings()
    settings = EmbeddingSettings(
        chunk_root=args.chunk_root or base_settings.chunk_root,
        qdrant_db_path=base_settings.qdrant_db_path,
        embedding_model=base_settings.embedding_model,
        vector_dimension=base_settings.vector_dimension,
        collection_name=base_settings.collection_name,
        embedding_batch_size=args.batch_size or base_settings.embedding_batch_size,
    )
    embed_all_chunks(settings)


if __name__ == "__main__":
    
    main()
