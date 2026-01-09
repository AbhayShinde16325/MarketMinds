"""
Response Builder for MarketMinds

This module orchestrates the full response flow:
- route the query
- gather context (API / documents)
- construct the prompt
- call the LLM
- return the final answer

This is the ONLY place where LLMs are invoked.
"""

from backend.app.config import config
from backend.app.chatbot.router import QueryRouter, QueryType
from backend.app.llm.llm_client import LLMClient
from backend.app.llm.prompt_templates import full_prompt
from backend.app.data_sources.financial_api import MarketDataClient, TickerResolver
from backend.app.rag.ingest import DocumentIngestor
from backend.app.rag.retriever import Retriever
from backend.app.rag.embeddings import DummyEmbeddingClient


class ResponseBuilder:
    """
    Builds grounded responses to user questions.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        # Core components
        self.router = QueryRouter()
        self.llm_client = llm_client

        # Live market data
        self.market_client = MarketDataClient()
        self.ticker_resolver = TickerResolver()

        # RAG components
        vector_store_path = config.VECTOR_STORE_DIR / "faiss_store.pkl"

        self.retriever = Retriever(
            embedding_client=DummyEmbeddingClient(),
            vector_store_path=vector_store_path,
        )

        self.ingestor = DocumentIngestor()

        # Ingest PDFs once
        raw_data_dir = config.RAW_DATA_DIR
        if not vector_store_path.exists():
            for pdf_file in raw_data_dir.glob("*.pdf"):
                chunks = self.ingestor.ingest_pdf(pdf_file)
                self.retriever.add_documents(chunks)

        # Demo fallback docs (safe)
        demo_docs = [
            "Apple reported strong revenue growth in 2023 driven by iPhone sales.",
            "The company increased its investments in artificial intelligence research.",
            "Apple's annual report highlighted supply chain diversification.",
        ]
        self.retriever.add_documents(demo_docs)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def build_response(self, question: str) -> str:
        query_type = self.router.route(question)

        # 1. Live market queries
        if query_type == QueryType.LIVE_MARKET:
            market_answer = self._handle_live_market_query(question)
            if market_answer:
                return market_answer
            # fallback to LLM if ticker not resolved

        # 2. Document / RAG queries
        if query_type == QueryType.DOCUMENT:
            context = self._get_rag_context(question)
            return self.llm_client.generate(
                prompt=full_prompt(question=question, context=context)
            )

        # 3. General knowledge (LLM fallback)
        return self.llm_client.generate(
            prompt=full_prompt(question=question)
        )

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _handle_live_market_query(self, question: str) -> str | None:
        ticker = self.ticker_resolver.resolve(question)

        if not ticker:
            return None

        try:
            data = self.market_client.get_stock_price(ticker)
        except Exception:
            return "I couldn't fetch live market data at the moment."

        return (
            f"{data['ticker']} is trading at {data['price']} {data['currency']} "
            f"(as of {data['timestamp']})."
        )

    def _get_rag_context(self, question: str) -> str:
        chunks = self.retriever.retrieve(question, top_k=3)
        if not chunks:
            return "No relevant documents found."
        return "\n\n".join(f"- {chunk}" for chunk in chunks)
