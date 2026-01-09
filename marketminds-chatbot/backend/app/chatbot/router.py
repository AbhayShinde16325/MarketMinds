from __future__ import annotations

from enum import Enum


class QueryType(Enum):
    LIVE_MARKET="live_market"
    DOCUMENT = "document"
    GENERAL = "general"


class QueryRouter:
    """
    Routes user queries to the correct data source.
    """

    def route(self, question: str) -> QueryType:
        q = question.lower()

        if any(word in q for word in ["price", "share", "stock", "market cap"]):
            return QueryType.LIVE_MARKET

        if any(word in q for word in ["report", "document", "pdf", "said"]):
            return QueryType.DOCUMENT

        return QueryType.GENERAL

