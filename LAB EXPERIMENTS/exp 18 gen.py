"""
Vector Database for Similarity-Based Document Retrieval
---------------------------------------------------------
Wraps document embedding + storage + retrieval behind one interface,
with three interchangeable backends:

    "faiss"  - Facebook AI Similarity Search. Local, extremely fast,
               best for large in-memory collections.
    "chroma" - ChromaDB. Local, persistent by default, adds metadata
               filtering and a simple document store on top of the index.
    "numpy"  - Pure numpy fallback. No extra dependencies. Useful for
               small collections, testing, or restricted environments.

Install (pick what you need):
    pip install sentence-transformers numpy
    pip install faiss-cpu          # for backend="faiss"
    pip install chromadb           # for backend="chroma"
"""

from __future__ import annotations
import json
import os
import numpy as np


# ----------------------------------------------------------------------
# Embedding model (shared across all backends)
# ----------------------------------------------------------------------
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        ).astype("float32")


# ----------------------------------------------------------------------
# Backend 1: FAISS
# ----------------------------------------------------------------------
class FaissBackend:
    """Uses IndexFlatIP (inner product) on normalized vectors == cosine similarity."""

    def __init__(self, dim: int):
        import faiss
        self.faiss = faiss
        self.index = faiss.IndexFlatIP(dim)
        self.documents: list[str] = []
        self.metadatas: list[dict] = []

    def add(self, embeddings: np.ndarray, documents: list[str], metadatas: list[dict]):
        self.index.add(embeddings)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)

    def search(self, query_embedding: np.ndarray, top_k: int):
        scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append({
                "document": self.documents[idx],
                "metadata": self.metadatas[idx],
                "similarity": float(score),
            })
        return results

    def persist(self, path: str):
        os.makedirs(path, exist_ok=True)
        self.faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "store.json"), "w") as f:
            json.dump({"documents": self.documents, "metadatas": self.metadatas}, f)

    def load(self, path: str):
        self.index = self.faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "store.json")) as f:
            data = json.load(f)
        self.documents = data["documents"]
        self.metadatas = data["metadatas"]


# ----------------------------------------------------------------------
# Backend 2: ChromaDB
# ----------------------------------------------------------------------
class ChromaBackend:
    """Chroma stores embeddings, documents, and metadata together and
    persists to disk automatically."""

    def __init__(self, dim: int, persist_path: str = "./chroma_store",
                 collection_name: str = "documents"):
        import chromadb
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )
        self._next_id = self.collection.count()

    def add(self, embeddings: np.ndarray, documents: list[str], metadatas: list[dict]):
        ids = [str(self._next_id + i) for i in range(len(documents))]
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        self._next_id += len(documents)

    def search(self, query_embedding: np.ndarray, top_k: int):
        result = self.collection.query(
            query_embeddings=[query_embedding.tolist()], n_results=top_k
        )
        results = []
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            # Chroma returns cosine *distance*; convert to similarity
            results.append({"document": doc, "metadata": meta, "similarity": 1 - dist})
        return results

    def persist(self, path: str = None):
        pass  # PersistentClient writes to disk automatically on add()

    def load(self, path: str):
        pass  # Reopening PersistentClient at the same path loads existing data


# ----------------------------------------------------------------------
# Backend 3: pure numpy fallback (no extra dependencies)
# ----------------------------------------------------------------------
class NumpyBackend:
    def __init__(self, dim: int):
        self.dim = dim
        self.matrix = np.zeros((0, dim), dtype="float32")
        self.documents: list[str] = []
        self.metadatas: list[dict] = []

    def add(self, embeddings: np.ndarray, documents: list[str], metadatas: list[dict]):
        self.matrix = np.vstack([self.matrix, embeddings]) if len(self.matrix) else embeddings
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)

    def search(self, query_embedding: np.ndarray, top_k: int):
        # vectors are pre-normalized, so dot product == cosine similarity
        scores = self.matrix @ query_embedding
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {
                "document": self.documents[i],
                "metadata": self.metadatas[i],
                "similarity": float(scores[i]),
            }
            for i in top_indices
        ]

    def persist(self, path: str):
        os.makedirs(path, exist_ok=True)
        np.save(os.path.join(path, "matrix.npy"), self.matrix)
        with open(os.path.join(path, "store.json"), "w") as f:
            json.dump({"documents": self.documents, "metadatas": self.metadatas}, f)

    def load(self, path: str):
        self.matrix = np.load(os.path.join(path, "matrix.npy"))
        with open(os.path.join(path, "store.json")) as f:
            data = json.load(f)
        self.documents = data["documents"]
        self.metadatas = data["metadatas"]


# ----------------------------------------------------------------------
# Public interface
# ----------------------------------------------------------------------
class VectorDatabase:
    BACKENDS = {"faiss": FaissBackend, "chroma": ChromaBackend, "numpy": NumpyBackend}

    def __init__(self, backend: str = "faiss", model_name: str = "all-MiniLM-L6-v2", **backend_kwargs):
        if backend not in self.BACKENDS:
            raise ValueError(f"backend must be one of {list(self.BACKENDS)}")
        self.embedder = Embedder(model_name)
        self.backend_name = backend
        self.backend = self.BACKENDS[backend](self.embedder.dim, **backend_kwargs)

    def add_documents(self, documents: list[str], metadatas: list[dict] | None = None):
        """Embed and store documents, each with optional metadata (e.g. {'source': 'file.pdf'})."""
        metadatas = metadatas or [{} for _ in documents]
        embeddings = self.embedder.encode(documents)
        self.backend.add(embeddings, documents, metadatas)
        print(f"Added {len(documents)} documents to {self.backend_name} store.")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Return the top_k documents most similar to the query."""
        query_embedding = self.embedder.encode([query])[0]
        return self.backend.search(query_embedding, top_k)

    def persist(self, path: str):
        self.backend.persist(path)

    def load(self, path: str):
        self.backend.load(path)


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    documents = [
        "The cat sat on the warm windowsill in the afternoon sun.",
        "Stock markets rallied today after inflation data came in lower than expected.",
        "Machine learning models can learn patterns from large datasets.",
        "She adopted a rescue dog from the local animal shelter.",
        "The Federal Reserve is expected to discuss interest rate changes.",
        "Neural networks are inspired by the structure of the human brain.",
        "He went hiking in the mountains over the weekend.",
        "Quarterly earnings reports showed strong growth in tech companies.",
    ]
    metadatas = [{"id": i, "topic": "misc"} for i in range(len(documents))]

    # Change to backend="chroma" for persistent storage + metadata filtering,
    # or backend="numpy" to run with zero extra dependencies.
    db = VectorDatabase(backend="faiss")
    db.add_documents(documents, metadatas)

    query = "How is the economy doing?"
    results = db.retrieve(query, top_k=3)

    print(f"\nQuery: {query}\n")
    for rank, r in enumerate(results, 1):
        print(f"  #{rank}  [{r['similarity']:.4f}]  {r['document']}")

    db.persist("./vector_store")
    print("\nSaved index to ./vector_store")
