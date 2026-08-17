"""
Domain-Specific Chatbot: LangChain + Vector Database
--------------------------------------------------------
A chatbot scoped to a specific domain (e.g. HR policy, legal, IT
support) that answers ONLY from documents in that domain, using:

    LangChain document loaders  -> load domain documents
    RecursiveCharacterTextSplitter -> chunk them
    HuggingFaceEmbeddings       -> embed chunks
    Chroma                      -> vector database (persisted to disk)
    create_stuff_documents_chain + create_retrieval_chain
                                 -> LangChain's current (LCEL-based) RAG pattern
    ChatAnthropic                -> the LLM

This is single-turn Q&A focused purely on domain-scoped retrieval and
answering. For multi-turn conversation memory (follow-up questions
that depend on earlier turns), see item 8 / langchain_chatbot.py,
which builds on this same pattern and adds ConversationBufferMemory.

*** IMPORTANT: sandbox caveat ***
This sandbox has no network access, so `langchain` could not be
installed or run here -- this file is NOT execution-verified, unlike
the earlier scripts in this series. The APIs below (create_retrieval_chain,
create_stuff_documents_chain) are LangChain's current recommended RAG
pattern as of early 2026, replacing the older, now-deprecated RetrievalQA
class. Install and run this on your own machine; if an import fails,
check your installed LangChain version's docs, since these APIs have
shifted before and may again.

Install:
    pip install langchain langchain-community langchain-chroma \
                langchain-anthropic langchain-huggingface \
                sentence-transformers chromadb anthropic
    export ANTHROPIC_API_KEY=your_key
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


class DomainChatbot:
    def __init__(self, domain_name: str, domain_instructions: str,
                 persist_dir: str = "./chroma_domain_store",
                 model: str = "claude-sonnet-4-6",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 500, chunk_overlap: int = 100, top_k: int = 4):
        """
        domain_name: short label (e.g. "HR Policy Assistant") used in the system prompt.
        domain_instructions: what the bot should and shouldn't do in this domain,
            e.g. "Only answer questions about employee leave, benefits, and
            reimbursement policy. Decline unrelated questions."
        """
        self.domain_name = domain_name

        # 1. Embeddings + Chroma vector database (persists to disk between runs)
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
            collection_name=domain_name.lower().replace(" ", "_"),
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})

        # 2. Chunking
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # 3. Domain-scoped system prompt. {context} is filled in by the
        # retrieval chain with the retrieved chunks for each question.
        system_prompt = (
            f"You are {domain_name}, a chatbot restricted to a specific domain.\n"
            f"{domain_instructions}\n\n"
            "Answer using ONLY the context below. If the answer isn't in the "
            "context, say you don't have that information -- do not guess or "
            "use outside knowledge.\n\nContext:\n{context}"
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # 4. LLM + the modern LangChain RAG chain: retriever -> stuff
        # documents into the prompt -> LLM. create_retrieval_chain wires
        # retrieval and generation together in one call.
        self.llm = ChatAnthropic(model=model, temperature=0)
        combine_docs_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, combine_docs_chain)

    def add_documents(self, path: str):
        """Load and index domain documents from a file or a directory of .txt files."""
        loader = TextLoader(path) if path.endswith(".txt") else \
            DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader)
        raw_docs = loader.load()
        chunks = self.splitter.split_documents(raw_docs)
        self.vectorstore.add_documents(chunks)
        print(f"[{self.domain_name}] Indexed {len(raw_docs)} document(s) "
              f"as {len(chunks)} chunks.")

    def ask(self, question: str) -> dict:
        """Answer a single question, scoped to this chatbot's domain."""
        result = self.rag_chain.invoke({"input": question})
        return {
            "answer": result["answer"],
            "sources": [
                {"source": doc.metadata.get("source"), "text": doc.page_content}
                for doc in result.get("context", [])
            ],
        }


# ----------------------------------------------------------------------
# Example: an HR policy assistant, scoped to only that domain
# ----------------------------------------------------------------------
if __name__ == "__main__":
    bot = DomainChatbot(
        domain_name="HR Policy Assistant",
        domain_instructions=(
            "You only answer questions about employee leave policy, benefits, "
            "and expense reimbursement. If asked about anything outside HR "
            "policy (e.g. general trivia, coding help), politely decline and "
            "explain you're scoped to HR topics only."
        ),
    )
    bot.add_documents("./hr_docs")  # a folder of .txt HR policy documents

    for question in [
        "How many paid vacation days do employees get per year?",
        "What's the capital of France?",  # out-of-domain, should decline
    ]:
        result = bot.ask(question)
        print(f"\nQ: {question}")
        print(f"A: {result['answer']}")
