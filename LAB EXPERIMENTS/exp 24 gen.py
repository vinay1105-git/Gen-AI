"""
Simple AI Assistant: Answering Questions from External Documents
----------------------------------------------------------------------
Deliberately minimal and self-contained (no imports from the other
files in this series) -- everything needed fits in one short file:

    1. Load a handful of documents (plain strings or .txt files)
    2. Embed them
    3. Given a question, find the most relevant document(s)
    4. Generate an answer grounded in that document

For chunking, multiple-document management, conversation memory, or
LangChain integration, see the more elaborate versions earlier in this
series (rag_pipeline.py, conversational_assistant.py, item 7/8 files).
This one is intentionally the "simple" version.

Install:
    pip install scikit-learn numpy      # works fully offline with these
    pip install anthropic               # optional, for real generated answers
"""

from __future__ import annotations
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class SimpleAssistant:
    def __init__(self, documents: list[str]):
        """documents: a list of raw text strings to answer questions from."""
        self.documents = documents
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    @classmethod
    def from_folder(cls, folder_path: str) -> "SimpleAssistant":
        """Convenience constructor: load every .txt file in a folder."""
        texts = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), encoding="utf-8") as f:
                    texts.append(f.read())
        return cls(texts)

    def most_relevant_document(self, question: str) -> tuple[str, float]:
        """Find the single document most relevant to the question."""
        question_vector = self.vectorizer.transform([question])
        similarities = (self.doc_vectors @ question_vector.T).toarray().flatten()
        best_index = int(np.argmax(similarities))
        return self.documents[best_index], float(similarities[best_index])

    def answer(self, question: str, use_llm: bool = True) -> str:
        """
        Answer a question grounded in the most relevant document.
        If an ANTHROPIC_API_KEY is set and use_llm=True, generates a real
        answer with Claude. Otherwise falls back to returning the most
        relevant document as-is, so this still works with zero API setup.
        """
        best_doc, score = self.most_relevant_document(question)

        if score == 0:
            return "I don't have any information about that in my documents."

        if use_llm and os.environ.get("ANTHROPIC_API_KEY"):
            return self._generate_with_llm(question, best_doc)

        return f"(no LLM configured -- most relevant document found:)\n{best_doc}"

    def _generate_with_llm(self, question: str, context: str) -> str:
        import anthropic
        client = anthropic.Anthropic()
        prompt = (
            f"Answer the question using only this context. If the context "
            f"doesn't contain the answer, say you don't know.\n\n"
            f"Context: {context}\n\nQuestion: {question}"
        )
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in response.content if b.type == "text")


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    documents = [
        "The Great Wall of China is over 13,000 miles long and was built "
        "over many centuries, primarily during the Ming Dynasty, to protect "
        "against invasions from northern nomadic groups.",

        "The Amazon rainforest produces about 20% of the world's oxygen and "
        "is home to roughly 10% of all known species on Earth. It spans "
        "nine countries in South America.",

        "The human brain contains approximately 86 billion neurons and "
        "consumes about 20% of the body's total energy despite making up "
        "only about 2% of body weight.",
    ]

    assistant = SimpleAssistant(documents)

    for question in [
        "How long is the Great Wall of China?",
        "How many neurons are in the human brain?",
        "What's the population of Japan?",  # not covered by any document
    ]:
        print(f"Q: {question}")
        print(f"A: {assistant.answer(question)}\n")
