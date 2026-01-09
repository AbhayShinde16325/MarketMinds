"""
PDF utilities for MarketMinds Chatbot.

Handles loading and text extraction from PDF Files.

"""

from pathlib import Path
from typing import List

from pypdf import PdfReader

def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract all text from a PDF file.

    Args:
        pdf_path (Path): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    reader = PdfReader(str(file_path))
    pages_text : List[str]=[]

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return "\n".join(pages_text)