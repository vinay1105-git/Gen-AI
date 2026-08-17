"""
Context-Aware Chatbot: LangChain + Retrieval + LLM
--------------------------------------------------------
A chatbot that resolves follow-up questions using conversation history
-- e.g. "What about the second one?" gets rewritten against prior
turns into a standalone question before retrieval runs.

Uses LangChain's current (non-deprecated) conversational RAG pattern:

    create_history_aware_retriever  -> rewrites a follow-up question
                                        into a standalone query using
                                        chat history, THEN retrieves
    create_stuff_documents_chain    -> generates an answer from the
                                        retrieved context
    create_retrieval_chain          -> wires the two together
    RunnableWithMessageHistory      -> manages chat history per session
                                        automatically across calls

This replaces the older `ConversationalRetrievalChain`, which LangChain
has deprecated in favor of this LCEL-based pattern.

This file is scoped to context-awareness specifically (item 8). For a
domain-restricted, single-turn version, see domain_chatbot.py (item 7).
For a fully offline, tested (non-LangChain) equivalent, see
conversational_assistant.py.

*** IMPORTANT: sandbox caveat ***
No network access here means `langchain` could not be installed or run
in this sandbox -- this file is NOT execution-verified. APIs reflect
LangChain's current recommended pattern as of early 2026; check your
installed version's docs if an import doesn't match.

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
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


class ContextAwareChatbot:
    def __init__(self, persist_dir: str = "./chroma_context_store",
                 model: str = "claude-sonnet-4-6",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 500, chunk_overlap: int = 100, top_k: int = 4):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore = Chroma(embedding_function=self.embeddings, persist_directory=persist_dir)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.llm = ChatAnthropic(model=model, temperature=0)

        # --- Step 1: history-aware retriever ---
        # Rewrites e.g. "what about that one?" into a standalone query
        # like "what are the return terms for the premium plan?" using
        # chat_history, BEFORE running retrieval. Without this step, a
        # pronoun-heavy follow-up would retrieve irrelevant documents,
        # since the retriever has no memory of its own.
        contextualize_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and the latest user question, "
                       "rewrite the question as a standalone question that "
                       "can be understood without the chat history. Do NOT "
                       "answer it -- only reformulate it if needed, otherwise "
                       "return it unchanged."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_prompt
        )

        # --- Step 2: answer generation from retrieved context ---
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer the user's question "
                       "using ONLY the context below. If you don't know based on "
                       "the context, say so.\n\nContext:\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        # --- Step 3: wire retrieval + generation together ---
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain)

        # --- Step 4: automatic per-session history management ---
        # RunnableWithMessageHistory injects and updates chat_history on
        # every call, keyed by session_id, so callers don't manage the
        # message list by hand.
        self._session_histories: dict[str, ChatMessageHistory] = {}
        self.conversational_chain = RunnableWithMessageHistory(
            self.rag_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    def _get_session_history(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self._session_histories:
            self._session_histories[session_id] = ChatMessageHistory()
        return self._session_histories[session_id]

    def add_documents(self, path: str):
        loader = TextLoader(path) if path.endswith(".txt") else \
            DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader)
        chunks = self.splitter.split_documents(loader.load())
        self.vectorstore.add_documents(chunks)
        print(f"Indexed {len(chunks)} chunks.")

    def chat(self, message: str, session_id: str = "default") -> dict:
        """Ask a question within a given conversation session. Chat history
        for that session_id is tracked and reused automatically."""
        result = self.conversational_chain.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}},
        )
        return {
            "answer": result["answer"],
            "sources": [doc.metadata.get("source") for doc in result.get("context", [])],
        }

    def reset_session(self, session_id: str = "default"):
        self._session_histories.pop(session_id, None)


# ----------------------------------------------------------------------
# Example: a follow-up question that only makes sense with chat history
# ----------------------------------------------------------------------
if __name__ == "__main__":
    bot = ContextAwareChatbot()
    bot.add_documents("./product_docs")  # e.g. docs about "Basic" and "Premium" plans

    print(bot.chat("What features does the Premium plan include?")["answer"])

    # "it" here only resolves correctly because create_history_aware_retriever
    # rewrites it against the prior turn before retrieving -- a plain
    # retriever with no history awareness would likely retrieve nothing
    # useful for the literal string "how much does it cost?"
    print(bot.chat("How much does it cost?")["answer"])
