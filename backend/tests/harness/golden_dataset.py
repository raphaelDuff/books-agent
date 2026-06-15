"""Golden labels for the opt-in live-eval layer.

Unlike the deterministic scenarios, these do not script any behaviour — the
*real* model decides. Two shapes:

- ``GOLDEN_INTENTS``: (question, expected_intent) for deterministic router
  accuracy (no LLM judge needed — a plain label comparison).
- ``GOLDEN_RAG``: (question, reference) for Ragas RAG-quality scoring of the
  real end-to-end graph. ``reference`` is a short natural-language description of
  a good answer; Ragas's judge compares against it.

Keep this set tiny — every entry costs real tokens.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.value_objects import Intent


@dataclass(frozen=True)
class GoldenIntent:
    question: str
    expected_intent: Intent


@dataclass(frozen=True)
class GoldenRag:
    question: str
    reference: str


GOLDEN_INTENTS: list[GoldenIntent] = [
    GoldenIntent("books published in the 1990s rated above 4.5", Intent.STRUCTURED),
    GoldenIntent("books by Haruki Murakami", Intent.STRUCTURED),
    GoldenIntent("something melancholic about memory and loss", Intent.SEMANTIC),
    GoldenIntent("a hopeful story about second chances", Intent.SEMANTIC),
    GoldenIntent("90s sci-fi with a strong female lead", Intent.HYBRID),
    GoldenIntent("highly-rated thrillers about heists and car chases", Intent.HYBRID),
]


GOLDEN_RAG: list[GoldenRag] = [
    GoldenRag(
        question="something melancholic about memory and loss",
        reference=(
            "Literary fiction with a reflective, melancholic tone exploring "
            "memory, grief, or loss."
        ),
    ),
    GoldenRag(
        question="90s sci-fi with a strong female lead",
        reference=(
            "Science-fiction novels published in the 1990s featuring a "
            "prominent, capable female protagonist."
        ),
    ),
]
