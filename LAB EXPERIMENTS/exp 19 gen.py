"""
Document Storage + Top-K Retrieval
------------------------------------
Builds on vector_database.py (VectorDatabase / Embedder) and adds the
parts a real document store needs:

  - Stable, explicit document IDs (auto-generated or user-supplied)
  - update(id, text)  and  delete(ids)     -- not just add + search
  - top_k(query, k)                        -- single-query retrieval
  - top_k_batch(queries, k)                -- batch retrieval, one pass
  - persist / load

Uses the same "numpy" backend as vector_database.py by default so it
runs with zero extra dependencies; swap embedder for sentence-transformers
in production (see Embedder in vector_database.py).

Install:
    pip install numpy scikit-learn          # minimum, for the demo
    pip install sentence-transformers       # for real semantic embeddings
"""

from __future__ import annotations
import json
import os
import uuid
import numpy as np


class DocumentStore:
    """
    Stores (id, text, metadata, embedding) tuples and supports
    top-k similarity retrieval, updates, and deletes.

    embed_fn: a callable(list[str]) -> np.ndarray of shape (n, dim),
    with rows pre-normalized so dot product == cosine similarity.
    Pass in vector_database.Embedder().encode for real semantic search,
    or use the built-in TF-IDF helper below for a dependency-free demo.
    """

    def __init__(self, embed_fn):
        self.embed_fn = embed_fn
        self.ids: list[str] = []
        self.texts: list[str] = []
        self.metadatas: list[dict] = []
        self.matrix: np.ndarray | None = None   # (n_docs, dim)
        self._id_to_row: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------
    def add(self, texts: list[str], ids: list[str] | None = None,
            metadatas: list[dict] | None = None) -> list[str]:
        """Embed and store new documents. Returns the assigned IDs."""
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        metadatas = metadatas or [{} for _ in texts]
        if len(set(ids) & set(self.ids)):
            raise ValueError("Duplicate ID(s) passed to add(); use update() instead.")

        embeddings = self.embed_fn(texts)
        start_row = len(self.ids)
        for i, (doc_id, text, meta) in enumerate(zip(ids, texts, metadatas)):
            self._id_to_row[doc_id] = start_row + i
        self.ids.extend(ids)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)
        self.matrix = (
            np.vstack([self.matrix, embeddings]) if self.matrix is not None else embeddings
        )
        return ids

    def update(self, doc_id: str, text: str, metadata: dict | None = None):
        """Re-embed and overwrite an existing document in place."""
        if doc_id not in self._id_to_row:
            raise KeyError(f"No document with id {doc_id!r}")
        row = self._id_to_row[doc_id]
        self.texts[row] = text
        if metadata is not None:
            self.metadatas[row] = metadata
        self.matrix[row] = self.embed_fn([text])[0]

    def delete(self, ids: list[str]):
        """Remove documents by ID and compact storage."""
        keep_rows = [i for i, doc_id in enumerate(self.ids) if doc_id not in set(ids)]
        self.ids = [self.ids[i] for i in keep_rows]
        self.texts = [self.texts[i] for i in keep_rows]
        self.metadatas = [self.metadatas[i] for i in keep_rows]
        self.matrix = self.matrix[keep_rows] if self.matrix is not None else None
        self._id_to_row = {doc_id: i for i, doc_id in enumerate(self.ids)}

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------
    def top_k(self, query: str, k: int = 5) -> list[dict]:
        """Return the k most similar documents to a single query."""
        if self.matrix is None or len(self.ids) == 0:
            return []
        query_vec = self.embed_fn([query])[0]
        scores = self.matrix @ query_vec
        k = min(k, len(self.ids))
        top_rows = np.argpartition(-scores, k - 1)[:k]
        top_rows = top_rows[np.argsort(-scores[top_rows])]
        return [
            {
                "id": self.ids[r],
                "text": self.texts[r],
                "metadata": self.metadatas[r],
                "similarity": float(scores[r]),
            }
            for r in top_rows
        ]

    def top_k_batch(self, queries: list[str], k: int = 5) -> list[list[dict]]:
        """Retrieve top-k results for many queries in one embedding pass
        (much faster than calling top_k() in a loop for large batches)."""
        if self.matrix is None or len(self.ids) == 0:
            return [[] for _ in queries]
        query_matrix = self.embed_fn(queries)          # (n_queries, dim)
        all_scores = query_matrix @ self.matrix.T       # (n_queries, n_docs)
        k = min(k, len(self.ids))

        results = []
        for scores in all_scores:
            top_rows = np.argpartition(-scores, k - 1)[:k]
            top_rows = top_rows[np.argsort(-scores[top_rows])]
            results.append([
                {
                    "id": self.ids[r],
                    "text": self.texts[r],
                    "metadata": self.metadatas[r],
                    "similarity": float(scores[r]),
                }
                for r in top_rows
            ])
        return results

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def persist(self, path: str):
        os.makedirs(path, exist_ok=True)
        if self.matrix is not None:
            np.save(os.path.join(path, "matrix.npy"), self.matrix)
        with open(os.path.join(path, "store.json"), "w") as f:
            json.dump({"ids": self.ids, "texts": self.texts, "metadatas": self.metadatas}, f)

    def load(self, path: str):
        matrix_path = os.path.join(path, "matrix.npy")
        self.matrix = np.load(matrix_path) if os.path.exists(matrix_path) else None
        with open(os.path.join(path, "store.json")) as f:
            data = json.load(f)
        self.ids = data["ids"]
        self.texts = data["texts"]
        self.metadatas = data["metadatas"]
        self._id_to_row = {doc_id: i for i, doc_id in enumerate(self.ids)}

    def __len__(self):
        return len(self.ids)


# ----------------------------------------------------------------------
# Dependency-free embedding function for the demo below.
# In production, replace with vector_database.Embedder().encode for
# real semantic (transformer-based) embeddings.
# ----------------------------------------------------------------------
def make_tfidf_embed_fn(corpus: list[str]):
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit(corpus)

    def embed_fn(texts: list[str]) -> np.ndarray:
        mat = vectorizer.transform(texts).toarray().astype("float32")
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return mat / norms

    return embed_fn


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    corpus = [
        "The cat sat on the warm windowsill in the afternoon sun.",
        "Stock markets rallied today after inflation data came in lower than expected.",
        "Machine learning models can learn patterns from large datasets.",
        "She adopted a rescue dog from the local animal shelter.",
        "The Federal Reserve is expected to discuss interest rate changes.",
        "Neural networks are inspired by the structure of the human brain.",
        "He went hiking in the mountains over the weekend.",
        "Quarterly earnings reports showed strong growth in tech companies.",
    ]

    # Fit the embedder's vocabulary on the initial corpus. (A real
    # transformer embedder needs no such fitting step.)
    embed_fn = make_tfidf_embed_fn(corpus)
    store = DocumentStore(embed_fn=embed_fn)

    ids = store.add(
        corpus,
        metadatas=[{"topic": "misc"} for _ in corpus],
    )
    print(f"Stored {len(store)} documents.\n")

    # Single-query top-k
    print("Single query: 'How is the economy doing?'")
    for r in store.top_k("How is the economy doing?", k=3):
        print(f"  [{r['similarity']:.4f}] ({r['id'][:8]}) {r['text']}")

    # Batch top-k: several queries in one pass
    print("\nBatch queries:")
    batch_results = store.top_k_batch(
        ["dog adoption", "neural network brain"], k=2
    )
    for query, results in zip(["dog adoption", "neural network brain"], batch_results):
        print(f"  Query: {query}")
        for r in results:
            print(f"    [{r['similarity']:.4f}] {r['text']}")

    # Update and delete
    store.update(ids[0], "The kitten napped on the sunny windowsill.")
    store.delete([ids[1]])  # remove the stock market document
    print(f"\nAfter update + delete: {len(store)} documents remain.")

    store.persist("./doc_store")
    print("Persisted to ./doc_store")
