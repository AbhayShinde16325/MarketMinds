"""RAG ingestion Pipeline for MarketMinds Chatbot.

this module handles the ingestion of documents into the RAG system.
-loading docs
-cleaning texts
-splitting into chunks

it does not :
-create embeddings
-store vectors
-call LLMs"""

from pathlib import Path
from backend.app.utils.pdf_utils import extract_text_from_pdf   
from typing import List

class DocumentIngestor:
    """responisble for ingesting and preprocessing docs for RAG"""

    def ingest_pdf(self, pdf_path:Path, chunk_size:int=500)->List[str]:
        """Ingest a PDF document and split into chunks suitable for RAG.
        Args:
            pdf_path (Path): Path to the PDF document.
            chunk_size (int): The size of each text chunk.
        Returns:
            List[str]: List of text chunks.
        """
        raw_text = extract_text_from_pdf(pdf_path)
        chunks = self.ingest_text(raw_text, chunk_size)

        return chunks
    def ingest_text(self,raw_text:str,chunk_size: int=500)->List[str]:
        """ingest raw text and split into chunks suitable for RAG.

        Args:
            raw_text (str): The raw text document to ingest.
            chunk_size (int): The size of each text chunk.
            
        Returns:    
            List[str]: List of text chunks.
        """
        cleaned_text = self._clean_text(raw_text)
        chunks = self._chunk_text(cleaned_text, chunk_size)

        return chunks
    
    def _clean_text(self,text:str)->str:
        """ clean raw text by removing whitespace and noise"""
        return " ".join(text.split())
    
    def _chunk_text(self,text:str,chunk_size:int)->List[str]:
        """split  text into fixed size chunks."""

        chunks=[]
        start=0

        while start<len(text):
            end=start+chunk_size
            chunk=text[start:end]
            chunks.append(chunk)
            start=end

        return chunks
    