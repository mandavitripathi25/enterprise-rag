import uuid
import chromadb
from sentence_transformers import SentenceTransformer

from . import config
from .document_loader import extract_text, chunk_text

_embedder = SentenceTransformer(config.EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=config.CHROMA_DIR)
_collection = _client.get_or_create_collection(
    name=config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
)


def _embed(texts: list[str]) -> list[list[float]]:
    return _embedder.encode(texts, normalize_embeddings=True).tolist()


def add_document(filename: str, data: bytes) -> int:
    pages = extract_text(filename, data)
    docs, metas, ids = [], [], []
    for text, page in pages:
        for i, chunk in enumerate(chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
            docs.append(chunk)
            metas.append({"source": filename, "page": page or 0, "chunk": i})
            ids.append(str(uuid.uuid4()))
    if not docs:
        return 0
    _collection.add(documents=docs, embeddings=_embed(docs), metadatas=metas, ids=ids)
    return len(docs)


def search(query: str, k: int = config.TOP_K) -> list[dict]:
    if _collection.count() == 0:
        return []
    res = _collection.query(query_embeddings=_embed([query]), n_results=k)
    return [
        {"text": d, "source": m["source"], "page": m["page"], "score": 1 - dist}
        for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


def list_documents() -> list[str]:
    metas = _collection.get(include=["metadatas"])["metadatas"]
    return sorted({m["source"] for m in metas})


def delete_document(filename: str) -> None:
    _collection.delete(where={"source": filename})
