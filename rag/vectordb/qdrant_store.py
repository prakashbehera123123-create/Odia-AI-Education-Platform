from __future__ import annotations

from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from configs.settings import COLLECTION_NAME, QDRANT_DB_PATH, VECTOR_DIMENSION
from scripts.utils.path_utils import ensure_dir


class QdrantStore:
    """Local Qdrant storage for dense chunk vectors."""

    def __init__(
        self,
        db_path: Path = QDRANT_DB_PATH,
        collection_name: str = COLLECTION_NAME,
        vector_dimension: int = VECTOR_DIMENSION,
    ) -> None:
        self.db_path = db_path
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension
        ensure_dir(db_path)
        self.client = QdrantClient(path=str(db_path))

    def close(self) -> None:
        self.client.close()

    def initialize_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_dimension,
                distance=Distance.COSINE,
            ),
        )

    def upload_vectors(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        batch_size: int = 64,
    ) -> None:
        if not (len(ids) == len(vectors) == len(payloads)):
            raise ValueError("ids, vectors, and payloads must have the same length.")

        self.initialize_collection()

        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            points = [
                PointStruct(id=point_id, vector=vector, payload=payload)
                for point_id, vector, payload in zip(
                    ids[start:end],
                    vectors[start:end],
                    payloads[start:end],
                )
            ]
            self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        self.initialize_collection()
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        return [
            {
                "id": str(point.id),
                "score": point.score,
                "payload": point.payload or {},
            }
            for point in response.points
        ]
