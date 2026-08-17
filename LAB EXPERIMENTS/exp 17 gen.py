"""
Semantic Search System (Cosine Similarity)
-------------------------------------------
A self-contained system that:
  1. Generates embeddings for a document collection and a query
  2. Ranks documents by cosine similarity to the query
  3. Supports two embedding backends:
       - TF-IDF (scikit-learn) -- no downloads, works fully offline
       - Sentence-Transformers -- deep-learning embeddings, needs a
         one-time model download

Install:
    pip install scikit-learn numpy
    pip install sentence-transformers   # optional, for the neural backend
"""

from __future__ import annotations
import numpy as np


# ----------------------------------------------------------------------
# Core math: cosine similarity, written out explicitly
# ----------------------------------------------------------------------
def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    cosine_similarity(A, B) = (A . B) / (||A|| * ||B||)

    Measures the angle between two vectors, ignoring magnitude.
    Range: -1 (opposite) to 1 (identical direction).
    For text embeddings, values are usually 0 to 1.
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def cosine_similarity_batch(matrix: np.ndarray, vec: np.ndarray) -> np.ndarray:
    """Vectorized cosine similarity between every row of `matrix` and `vec`."""
    matrix_norms = np.linalg.norm(matrix, axis=1)
    vec_norm = np.linalg.norm(vec)
    denom = matrix_norms * vec_norm
    denom[denom == 0] = 1e-10  # avoid divide-by-zero
    return (matrix @ vec) / denom


# ----------------------------------------------------------------------
# Embedding backends
# ----------------------------------------------------------------------
class TfidfEmbedder:
    """Classical sparse embeddings. Fast, offline, good baseline."""

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._fitted = False

    def fit(self, documents: list[str]):
        self.doc_matrix = self.vectorizer.fit_transform(documents).toarray()
        self._fitted = True
        return self.doc_matrix

    def embed_query(self, query: str) -> np.ndarray:
        if not self._fitted:
            raise ValueError("Call fit(documents) before embedding queries.")
        return self.vectorizer.transform([query]).toarray()[0]


class NeuralEmbedder:
    """Dense embeddings from a pretrained transformer model."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def fit(self, documents: list[str]) -> np.ndarray:
        self.doc_matrix = self.model.encode(documents, convert_to_numpy=True)
        return self.doc_matrix

    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode([query], convert_to_numpy=True)[0]


# ----------------------------------------------------------------------
# Semantic search system
# ----------------------------------------------------------------------
class SemanticSearchSystem:
    def __init__(self, backend: str = "tfidf"):
        """
        backend: "tfidf" (offline, sparse) or "neural" (sentence-transformers)
        """
        if backend == "tfidf":
            self.embedder = TfidfEmbedder()
        elif backend == "neural":
            self.embedder = NeuralEmbedder()
        else:
            raise ValueError("backend must be 'tfidf' or 'neural'")

        self.documents: list[str] = []
        self.doc_embeddings: np.ndarray | None = None

    def index_documents(self, documents: list[str]):
        """Embed and store the document collection."""
        self.documents = documents
        self.doc_embeddings = self.embedder.fit(documents)
        print(f"Indexed {len(documents)} documents "
              f"({self.doc_embeddings.shape[1]}-dim embeddings)")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Embed the query and rank all documents by cosine similarity."""
        if self.doc_embeddings is None:
            raise ValueError("No documents indexed. Call index_documents() first.")

        query_embedding = self.embedder.embed_query(query)
        scores = cosine_similarity_batch(self.doc_embeddings, query_embedding)

        ranked_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {
                "rank": rank + 1,
                "document": self.documents[i],
                "similarity": round(float(scores[i]), 4),
            }
            for rank, i in enumerate(ranked_indices)
        ]


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

    # Swap backend="tfidf" -> backend="neural" for deep-learning embeddings
    system = SemanticSearchSystem(backend="tfidf")
    system.index_documents(corpus)

    query = "How is the economy doing?"
    results = system.search(query, top_k=3)

    print(f"\nQuery: {query}\n")
    for r in results:
        print(f"  #{r['rank']}  [{r['similarity']:.4f}]  {r['document']}")
