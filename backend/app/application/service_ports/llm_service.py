from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from app.domain.entities.book import BookDomain
from app.domain.value_objects import Intent


@dataclass(frozen=True)
class IntentClassification:
    """The router's decision for a book question.

    ``sql`` is a single read-only ``SELECT`` against the ``books`` table, present
    only when ``intent`` is STRUCTURED or HYBRID. ``semantic_query`` is a rewritten
    query for vector search, present for SEMANTIC or HYBRID.
    """

    intent: Intent
    semantic_query: str = ""
    sql: str | None = None
    reasoning: str = ""


@dataclass(frozen=True)
class RankedPick:
    """A book chosen by the reranker, with its one-line justification."""

    book: BookDomain
    justification: str


class LLMService(ABC):
    """Capability port for the language-model work the agent performs."""

    @abstractmethod
    async def classify(self, question: str) -> IntentClassification:
        """Classify intent and extract a SQL filter and/or a semantic query."""
        raise NotImplementedError

    @abstractmethod
    async def repair_sql(self, sql: str, error: str) -> str:
        """Return a corrected ``SELECT`` given the failed SQL and the DB error."""
        raise NotImplementedError

    @abstractmethod
    async def rank_and_justify(
        self, question: str, candidates: Sequence[BookDomain], limit: int
    ) -> list[RankedPick]:
        """Rerank candidates for the question and justify each of the top picks."""
        raise NotImplementedError
