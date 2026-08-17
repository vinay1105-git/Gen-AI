"""
End-to-End RAG Pipeline
--------------------------
Ties together every stage into one system:

    Load documents (files/folders/raw text)
        -> Chunk into overlapping passages
        -> Embed each chunk
        -> Store in a vector index
        -> Retrieve top-k chunks for a question
        -> Generate a grounded answer with citations

Built on document_store.py (DocumentStore) and rag_qa_system.py
(build_prompt, generate_fn implementations) from earlier steps.

Install:
    pip install numpy scikit-learn                # minimum, for the demo
    pip install sentence-transformers              # real semantic embeddings
    pip install anthropic                          # real LLM generation
"""

from __future__ import annotations
import os
import glob

from document_store import DocumentStore, make_tfidf_embed_fn
from rag_qa_system import build_prompt, make_extractive_generate_fn, make_anthropic_generate_fn


# ----------------------------------------------------------------------
# Stage 1: Document loading
# ----------------------------------------------------------------------
def load_documents(source) -> list[dict]:
    """
    Accepts:
      - a single file path (.txt)
      - a directory path (loads all .txt files inside)
      - a list of raw strings (treated as already-loaded documents)
    Returns a list of {"text": ..., "source": ...} dicts.

    For PDFs or Word docs, extract their text first (see the pdf/docx
    skills for robust extraction) and pass the resulting strings in
    as a list here.
    """
    if isinstance(source, list):
        return [{"text": t, "source": f"raw_doc_{i}"} for i, t in enumerate(source)]

    if os.path.isdir(source):
        paths = sorted(glob.glob(os.path.join(source, "*.txt")))
    elif os.path.isfile(source):
        paths = [source]
    else:
        raise ValueError(f"'{source}' is not a valid path or list of strings")

    docs = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            docs.append({"text": f.read(), "source": os.path.basename(path)})
    return docs


# ----------------------------------------------------------------------
# Stage 2: Chunking
# ----------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Splits text into overlapping word-based chunks.

    chunk_size: target number of words per chunk. Smaller chunks give
      more precise retrieval but less surrounding context per chunk.
    overlap: words shared between consecutive chunks, so an idea that
      spans a chunk boundary doesn't get cut off and lost entirely.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    step = chunk_size - overlap
    while start < len(words):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
        start += step
    return chunks


def chunk_documents(docs: list[dict], chunk_size: int = 500, overlap: int = 100) -> tuple[list[str], list[dict]]:
    """
    Chunks every document and returns (chunk_texts, chunk_metadatas),
    where each metadata dict tracks which source document and chunk
    index a chunk came from -- essential for citing answers back to
    their original document, not just a passage number.
    """
    all_chunks, all_metas = [], []
    for doc in docs:
        chunks = chunk_text(doc["text"], chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metas.append({"source": doc["source"], "chunk_index": i, "total_chunks": len(chunks)})
    return all_chunks, all_metas


# ----------------------------------------------------------------------
# Stages 3-5: Embed + store, retrieve, generate -- wired into one pipeline
# ----------------------------------------------------------------------
class RAGPipeline:
    def __init__(self, embed_fn, generate_fn, chunk_size: int = 500,
                 chunk_overlap: int = 100, top_k: int = 3):
        self.store = DocumentStore(embed_fn=embed_fn)
        self.generate_fn = generate_fn
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

    def index(self, source):
        """Load -> chunk -> embed -> store, in one call."""
        docs = load_documents(source)
        chunks, metas = chunk_documents(docs, self.chunk_size, self.chunk_overlap)
        self.store.add(chunks, metadatas=metas)
        print(f"Indexed {len(docs)} document(s) as {len(chunks)} chunks.")

    def ask(self, question: str, top_k: int | None = None) -> dict:
        """Retrieve -> generate, in one call."""
        retrieved = self.store.top_k(question, k=top_k or self.top_k)
        if not retrieved:
            return {"answer": "No documents indexed yet.", "sources": []}

        prompt = build_prompt(question, retrieved)
        answer_text = self.generate_fn(prompt)

        return {
            "answer": answer_text,
            "sources": [
                {
                    "source": r["metadata"].get("source"),
                    "chunk_index": r["metadata"].get("chunk_index"),
                    "text": r["text"],
                    "similarity": r["similarity"],
                }
                for r in retrieved
            ],
        }


# ----------------------------------------------------------------------
# Demo: build sample docs on disk, run the full pipeline end-to-end
# ----------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs("./sample_docs", exist_ok=True)
    sample_docs = {
        "eiffel_tower.txt": (
            "The Eiffel Tower is a wrought-iron lattice tower located in Paris, France. "
            "It was designed by engineer Gustave Eiffel and completed in 1889 for the "
            "World's Fair. The tower stands 330 meters tall and was the tallest man-made "
            "structure in the world for 41 years, until the Chrysler Building was finished "
            "in New York in 1930. Today it remains one of the most visited paid monuments "
            "in the world, attracting millions of tourists annually."
        ),
        "python_history.txt": (
            "Python is a high-level programming language created by Guido van Rossum. "
            "Development began in the late 1980s and the first version was released in "
            "1991. Python emphasizes code readability with its notable use of significant "
            "whitespace. It has grown into one of the most popular programming languages "
            "in the world, widely used in web development, data science, automation, and "
            "artificial intelligence research."
        ),
        "climate.txt": (
            "Climate change refers to long-term shifts in temperatures and weather "
            "patterns. Since the 1800s, human activities have been the main driver of "
            "climate change, primarily due to the burning of fossil fuels like coal, "
            "oil, and gas, which produces heat-trapping greenhouse gases. Rising global "
            "temperatures have led to more frequent extreme weather events, rising sea "
            "levels, and disruptions to ecosystems worldwide."
        ),
    }
    for filename, content in sample_docs.items():
        with open(os.path.join("./sample_docs", filename), "w") as f:
            f.write(content)

    # Fit the TF-IDF vocabulary on the raw documents before chunking/indexing.
    # (A real transformer embedder needs no such pre-fit step -- just pass
    # vector_database.Embedder().encode as embed_fn instead.)
    embed_fn = make_tfidf_embed_fn(list(sample_docs.values()))

    # Swap for make_anthropic_generate_fn() for real generated answers.
    generate_fn = make_extractive_generate_fn()

    pipeline = RAGPipeline(
        embed_fn=embed_fn,
        generate_fn=generate_fn,
        chunk_size=50,     # small on purpose so these short demo docs actually split into chunks
        chunk_overlap=10,
        top_k=2,
    )
    pipeline.index("./sample_docs")

    for question in [
        "When was the Eiffel Tower completed?",
        "Who created Python and when?",
        "What causes climate change?",
    ]:
        result = pipeline.ask(question)
        print(f"\nQ: {question}")
        print(f"A: {result['answer']}")
        print("Sources:")
        for s in result["sources"]:
            print(f"  [{s['similarity']:.4f}] {s['source']} (chunk {s['chunk_index']})")
