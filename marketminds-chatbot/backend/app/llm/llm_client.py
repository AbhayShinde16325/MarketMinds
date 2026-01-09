"""
LLM Client for MarketMinds

This module defines a strict interface for interacting with
Large Language Models (LLMs), and a concrete Ollama implementation.
"""

import subprocess
from typing import Optional


class LLMClient:
    """
    Base LLM client abstraction.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate a response from the LLM.
        """
        raise NotImplementedError(
            "LLMClient.generate() must be implemented"
        )


class OllamaLLMClient(LLMClient):
    """
    LLM client that uses Ollama for local inference.
    """

    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        try:    
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                text=True,
                encoding="utf-8",        # ✅ force UTF-8
                errors="ignore",  # ✅ ignore encoding errors
                capture_output=True,
                check=True,
            )
            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            return f"LLM execution failed: {e.stderr}"
