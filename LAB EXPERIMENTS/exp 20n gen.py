"""
Retrieval-Augmented Generation (RAG) Question Answering
----------------------------------------------------------
Combines the DocumentStore (retrieval) from document_store.py with an
LLM (generation) to answer questions grounded in your own documents.

Flow:
    question -> embed -> retrieve top-k relevant chunks
             -> build a prompt with those chunks as context
             -> LLM generates an answer using ONLY that context
             -> return answer + which sources it came from

Install:
    pip install numpy scikit-learn              # minimum, for the demo
    pip install sentence-transformers            # for real semantic retrieval
    pip install anthropic                        # for real LLM generation
"""

from __future__ import annotations
from document_store import DocumentStore, make_tfidf_embed_fn


# ----------------------------------------------------------------------
# Prompt construction
# ----------------------------------------------------------------------
def build_prompt(question: str, retrieved: list[dict]) -> str:
    """
    Builds a grounded prompt: numbered context passages + explicit
    instructions to answer only from that context and cite sources.
    Keeping citations tied to passage numbers is what lets the caller
    trace an answer back to specific documents.
    """
    context_block = "\n\n".join(
        f"[{i+1}] {r['text']}" for i, r in enumerate(retrieved)
    )
    return f"""Answer the question using ONLY the context passages below.
Cite the passage number(s) you used, like [1] or [1][3].
If the context does not contain the answer, say so plainly instead of guessing.

Context:
{context_block}

Question: {question}

Answer:"""


# ----------------------------------------------------------------------
# RAG system
# ----------------------------------------------------------------------
class RAGSystem:
    def __init__(self, document_store: DocumentStore, generate_fn, top_k: int = 3):
        """
        document_store: a DocumentStore instance already populated with documents.
        generate_fn: callable(prompt: str) -> str. Plug in any LLM here
                     (Claude, GPT, a local model, etc.) -- see examples below.
        top_k: number of passages to retrieve as context per question.
        """
        self.store = document_store
        self.generate_fn = generate_fn
        self.top_k = top_k

    def answer(self, question: str) -> dict:
        retrieved = self.store.top_k(question, k=self.top_k)
        if not retrieved:
            return {"answer": "No documents indexed yet.", "sources": []}

        prompt = build_prompt(question, retrieved)
        answer_text = self.generate_fn(prompt)

        return {
            "answer": answer_text,
            "sources": [
                {"id": r["id"], "text": r["text"], "similarity": r["similarity"]}
                for r in retrieved
            ],
        }


# ----------------------------------------------------------------------
# generate_fn implementations (pick one, or write your own)
# ----------------------------------------------------------------------
def make_anthropic_generate_fn(model: str = "claude-sonnet-4-6", api_key: str | None = None):
    """
    Real LLM generation via the Anthropic API.
    Requires: pip install anthropic, and ANTHROPIC_API_KEY set (or pass api_key).
    Not used in the demo below since this sandbox has no network access --
    use this in your own environment.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)  # reads ANTHROPIC_API_KEY if None

    def generate_fn(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    return generate_fn


def make_extractive_generate_fn():
    """
    Dependency-free stand-in for an LLM: no real language generation,
    just returns the most relevant retrieved passage(s) verbatim with
    their citation. Useful for testing the retrieval/prompt plumbing
    without an API key or network access -- NOT a substitute for a
    real LLM's synthesis and reasoning.
    """
    def generate_fn(prompt: str) -> str:
        # Pull the context passages back out of the prompt and just
        # return passage [1] as a stand-in "answer".
        context_start = prompt.index("Context:\n") + len("Context:\n")
        context_end = prompt.index("\n\nQuestion:")
        first_passage = prompt[context_start:context_end].split("\n\n")[0]
        return f"{first_passage} (extractive stand-in answer, not a real generated response)"

    return generate_fn


# ----------------------------------------------------------------------
# Demo (uses the dependency-free extractive stand-in so it runs offline)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    documents = [
        "The Eiffel Tower was completed in 1889 and stands 330 meters tall.",
        "Photosynthesis converts sunlight, water, and carbon dioxide into glucose and oxygen.",
        "The Federal Reserve raised interest rates by 0.25% in its March meeting to combat inflation.",
        "Python was created by Guido van Rossum and first released in 1991.",
        "The human heart beats approximately 100,000 times per day.",
        "Machine learning models improve their performance through exposure to training data.",
    ]

    embed_fn = make_tfidf_embed_fn(documents)
    store = DocumentStore(embed_fn=embed_fn)
    store.add(documents)

    # Swap this for make_anthropic_generate_fn() to get real generated answers
    generate_fn = make_extractive_generate_fn()
    rag = RAGSystem(document_store=store, generate_fn=generate_fn, top_k=2)

    questions = [
        "When was the Eiffel Tower built?",
        "Who created Python?",
    ]
    for q in questions:
        result = rag.answer(q)
        print(f"Q: {q}")
        print(f"A: {result['answer']}")
        print("Sources:")
        for s in result["sources"]:
            print(f"  [{s['similarity']:.4f}] {s['text']}")
        print()
