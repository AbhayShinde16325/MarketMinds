"""
Retriever module with FAISS persistence
"""

from typing import List
from pathlib import Path
import pickle
import faiss
import numpy as np
from backend.app.rag.embeddings import EmbeddingClient


class Retriever:
    """
    FAISS-backed retriever with persistence.
    """

    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_store_path: Path,
    ) -> None:
        self.embedding_client = embedding_client
        self.vector_store_path = vector_store_path

        self.text_chunks: List[str] = []
        self.index = None

        if self.vector_store_path.exists():
            self._load()
        else:
            self._initialize_index()

    def _initialize_index(self):
        # We use 1-dim dummy embeddings for now
        self.index = faiss.IndexFlatL2(1)

    def add_documents(self, chunks: List[str]) -> None:
        vectors = self.embedding_client.embed(chunks)

        if not vectors:
            return

        faiss_vectors = [v for v in vectors]
        self.index.add(np.array(faiss_vectors))

        self.text_chunks.extend(chunks)
        self._save()

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        query_vector = self.embedding_client.embed([query])[0]

        query_np = np.array([query_vector], dtype="float32")

        distances, indices = self.index.search(query_np, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])

        return results

    def _save(self):
        with open(self.vector_store_path, "wb") as f:
            pickle.dump(
                {
                    "index": self.index,
                    "chunks": self.text_chunks,
                },
                f,
            )

    def _load(self):
        with open(self.vector_store_path, "rb") as f:
            data = pickle.load(f)
            self.index = data["index"]
            self.text_chunks = data["chunks"]
