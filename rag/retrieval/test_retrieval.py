from __future__ import annotations

import argparse

from configs.settings import EmbeddingSettings
from rag.embeddings.embedder import Embedder
from rag.vectordb.qdrant_store import QdrantStore


def search_query(query: str, top_k: int = 5) -> list[dict]:
    settings = EmbeddingSettings()
    embedder = Embedder(settings.embedding_model)
    store = QdrantStore(
        db_path=settings.qdrant_db_path,
        collection_name=settings.collection_name,
        vector_dimension=settings.vector_dimension,
    )
    try:
        query_vector = embedder.embed_text(query)
        return store.search(query_vector, top_k=top_k)
    finally:
        store.close()


def print_results(results: list[dict]) -> None:
    for index, result in enumerate(results, start=1):
        payload = result["payload"]
        print(f"\nResult {index} | score={result['score']:.4f}")
        print(
            "class={class_name} subject={subject} book={book} page={page}".format(
                class_name=payload.get("class"),
                subject=payload.get("subject"),
                book=payload.get("book"),
                page=payload.get("page"),
            )
        )
        print(f"source_file={payload.get('source_file')}")
        print(payload.get("text", ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test retrieval from local Qdrant.")
    parser.add_argument("query", help="User query to search for.")
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = search_query(args.query, top_k=args.top_k)
    print_results(results)


if __name__ == "__main__":
    main()
