"""Prompt templates for MarketMinds Chatbot LLM interactions.
This module contains all the system and user prompt templates used in interactions with large language models (LLMs)."""

from typing import Optional

def system_prompt() -> str:
    """
    System-level instructions for the LLM.
    """
    return (
        "You are MarketMinds, an advanced AI assistant for market and financial analysis.\n"
        "Follow these rules strictly:\n"
        "1. If the provided CONTEXT contains relevant information, you MUST base your answer on it.\n"
        "2. If the CONTEXT does NOT contain sufficient information, you MAY use your general knowledge.\n"
        "3. If you use general knowledge, clearly state that the answer is based on general knowledge, not the documents.\n"
        "4. Do NOT contradict or override information found in the CONTEXT.\n"
        "5. Do NOT fabricate numbers, dates, or events.\n"
        "6. Be concise, factual, and clear.\n"
    )


def user_prompt(question: str) -> str:
    """Format the user's question into a prompt for the LLM.
    Args:
        question (str): The user's question.
        
    Returns:
        str: The formatted user prompt.
    """
    return f"Question:\n{question}"

def full_prompt(question: str, context: Optional[str] = None) -> str:
    """
    combines system and user prompts into a full prompt for the LLM.

    Args:
        question (str): The user's question.
        context (Optional[str]): Additional context to provide to the LLM.
    Returns:
        str: The complete prompt for the LLM.    
    """
    prompt_parts = [system_prompt()]

    if context:
        prompt_parts.append(f"Context:\n{context}")

    prompt_parts.append(user_prompt(question))

    return "\n\n".join(prompt_parts)   