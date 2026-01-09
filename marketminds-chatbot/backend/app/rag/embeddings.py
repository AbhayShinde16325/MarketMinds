""" Embeddings module for MarketMinds Chatbot.

This module defines how text chunks are converted into 
vector embeddings.

At this stage:
-embeddings are stubbed
- no external models are called
"""
from typing import List

class EmbeddingClient:
    """Base embeddding client interface."""

    def embed(self,texts: List[str])->List[List[float]]:
        """Convert a list of texts into their corresponding embeddings.
        
        Args:
            texts (List[str]): List of text chunks to embed.
        
        Returns:
            List[List[float]]: List of embeddings, each represented as a list of floats.
        
        """

        raise NotImplementedError(
            "EmbeddingClient.embed() must be implemented."
        )
    
class DummyEmbeddingClient(EmbeddingClient):
        """dummy embedding client for testing the pipeline"""
        def embed(self, texts: List[str]) -> List[List[float]]:
             """Generate dummy embeddings for the given texts."""
             embeddings=[]

             for text in texts:
                  #fake deterministic embedding
                  vector = [float(len(text))]
                  embeddings.append(vector)

                 

             return embeddings