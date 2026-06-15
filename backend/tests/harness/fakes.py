"""Scriptable, recording test doubles for the harness.

These extend the inline fakes in ``tests/test_nodes.py`` with two capabilities:

- **scripted queues** — responses are consumed per call (``repairs`` /
  ``sql_steps``), and over-consumption *raises* so a graph that calls a
  dependency more often than scripted fails loudly rather than silently
  replaying stale data;
- **call recording** — every call is appended to ``self.calls`` so metrics can
  assert behaviour (e.g. "``repair_sql`` was called exactly once").

They are duck-typed against the ports (not ABC subclasses): nodes only read
deps from ``config['configurable']`` and never type-check them, which keeps the
test doubles entirely inside ``tests/`` (inward dependency rule).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from app.application.service_ports.llm_service import IntentClassification, RankedPick
from app.domain.entities.book import BookDomain
from tests.harness.types import Scenario, SqlStep


def make_book(isbn: str, title: str = "T", description: str = "D") -> BookDomain:
    """Minimal valid book (lifted from tests/test_nodes.py:make_book)."""
    return BookDomain(isbn13=isbn, title=title, authors="A", description=description)


class ScriptedLLM:
    """LLMService double driven by a scenario's scripted decisions."""

    def __init__(
        self,
        classification: IntentClassification,
        repairs: Sequence[str] = (),
        ranked: Sequence[RankedPick] | None = None,
    ) -> None:
        self._classification = classification
        self._repairs = list(repairs)
        self._repair_i = 0
        self._ranked = list(ranked) if ranked is not None else None
        self.calls: list[tuple[str, Any]] = []

    async def classify(self, question: str) -> IntentClassification:
        self.calls.append(("classify", question))
        return self._classification

    async def repair_sql(self, sql: str, error: str) -> str:
        self.calls.append(("repair_sql", (sql, error)))
        if self._repair_i >= len(self._repairs):
            raise AssertionError(
                f"repair_sql called {self._repair_i + 1}x but only "
                f"{len(self._repairs)} repair(s) scripted"
            )
        fixed = self._repairs[self._repair_i]
        self._repair_i += 1
        return fixed

    async def rank_and_justify(
        self, question: str, candidates: Sequence[BookDomain], limit: int
    ) -> list[RankedPick]:
        self.calls.append(("rank_and_justify", [c.isbn13 for c in candidates]))
        if self._ranked is not None:
            return list(self._ranked)
        return [
            RankedPick(book=b, justification="scripted") for b in candidates[:limit]
        ]

    @property
    def repair_calls(self) -> int:
        return sum(1 for name, _ in self.calls if name == "repair_sql")


class ScriptedBookRepo:
    """BookRepository double walking a scenario's SQL timeline."""

    def __init__(self, sql_steps: Sequence[SqlStep] = ()) -> None:
        self._steps = list(sql_steps)
        self._i = 0
        self.calls: list[str] = []

    async def execute_select(self, sql: str) -> Sequence[BookDomain]:
        self.calls.append(sql)
        if self._i >= len(self._steps):
            raise AssertionError(
                f"execute_select called {self._i + 1}x but only "
                f"{len(self._steps)} sql_step(s) scripted"
            )
        step = self._steps[self._i]
        self._i += 1
        if step.error is not None:
            raise ValueError(step.error)
        return list(step.rows)


class ScriptedVectorRepo:
    """BookVectorRepository double; records the allowlist it received."""

    def __init__(self, books: Sequence[BookDomain] = ()) -> None:
        self._books = list(books)
        self.last_allowlist: Sequence[str] | None | str = "unset"
        self.calls: list[dict[str, Any]] = []

    async def search_by_vector(
        self,
        vector: list[float],
        limit: int,
        isbn13_allowlist: Sequence[str] | None = None,
    ) -> Sequence[BookDomain]:
        self.last_allowlist = isbn13_allowlist
        self.calls.append({"limit": limit, "allowlist": isbn13_allowlist})
        return list(self._books)


class ScriptedEmbeddings:
    """EmbeddingsService double returning a fixed vector."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return [0.1, 0.2, 0.3]


@dataclass
class ScriptedDeps:
    """The four scripted doubles for one scenario run."""

    llm: ScriptedLLM
    book_repo: ScriptedBookRepo
    vector_repo: ScriptedVectorRepo
    embeddings: ScriptedEmbeddings


def build_deps(scenario: Scenario) -> ScriptedDeps:
    return ScriptedDeps(
        llm=ScriptedLLM(
            classification=scenario.classify,
            repairs=scenario.repairs,
            ranked=scenario.ranked,
        ),
        book_repo=ScriptedBookRepo(scenario.sql_steps),
        vector_repo=ScriptedVectorRepo(scenario.semantic_books),
        embeddings=ScriptedEmbeddings(),
    )


def cfg(*, thread_id: str, deps: ScriptedDeps) -> dict[str, Any]:
    """Assemble a RunnableConfig. ``thread_id`` is required: the graph compiles
    with a ``MemorySaver`` checkpointer (tests/test_nodes.py uses ``cfg`` too,
    but the full graph needs a thread)."""
    return {
        "configurable": {
            "thread_id": thread_id,
            "llm": deps.llm,
            "book_repo": deps.book_repo,
            "vector_repo": deps.vector_repo,
            "embeddings": deps.embeddings,
        }
    }
