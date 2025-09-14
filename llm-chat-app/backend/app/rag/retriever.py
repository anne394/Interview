from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import settings
from typing import List
import uuid

# Qdrant client (HTTP)
client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=False, api_key=settings.QDRANT_API_KEY)

def ensure_collection(vector_size: int = 1536):
    try:
        client.get_collection(settings.QDRANT_COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )

def add_documents_to_qdrant(docs: List[dict], vector_size: int = 1536):
    """
    docs: list of {"id": id_str, "text": "...", "meta": {...}}
    """
    ensure_collection(vector_size=vector_size)
    points = []
    for d in docs:
        points.append(
            qmodels.PointStruct(
                id=d.get("id", str(uuid.uuid4())),
                vector=d["embedding"],
                payload={"text": d["text"], "meta": d.get("meta", {})},
            )
        )
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)

def semantic_search(query_embedding: List[float], limit: int = 3):
    ensure_collection()
    hits = client.search(collection_name=settings.QDRANT_COLLECTION, query_vector=query_embedding, limit=limit)
    results = []
    for h in hits:
        results.append({"id": h.id, "score": h.score, "text": h.payload.get("text"), "meta": h.payload.get("meta")})
    return results
