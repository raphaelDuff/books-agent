"""Golden labels for the opt-in live-eval layer.

Unlike the deterministic scenarios, these do not script any behaviour — the
*real* model decides. Two shapes:

- ``GOLDEN_INTENTS``: (question, expected_intent) for deterministic router
  accuracy (no LLM judge needed — a plain label comparison).
- ``GOLDEN_RAG``: (question, reference) for Ragas RAG-quality scoring of the
  real end-to-end graph. ``reference`` is a short natural-language description of
  a good answer; Ragas's judge compares against it.

Every entry costs real tokens (one graph run + four Ragas judge calls), so keep
the set focused. It is intentionally weighted toward thematic/semantic queries —
the catalogue's strength is description embeddings — with a couple of
hybrid/structured shapes to exercise the SQL filter too. Spanning intents this
way makes the per-metric averages meaningful rather than n=1 noise.
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
    # --- semantic / thematic (the catalogue's strength) ---
    GoldenRag(
        question="something melancholic about memory and loss",
        reference=(
            "Literary fiction with a reflective, melancholic tone exploring "
            "memory, grief, or loss."
        ),
    ),
    GoldenRag(
        question="a hopeful story about second chances and starting over",
        reference=(
            "Uplifting fiction about renewal, redemption, or starting life over "
            "after hardship."
        ),
    ),
    GoldenRag(
        question="a dark psychological thriller with an unreliable narrator",
        reference=(
            "A tense psychological thriller with twists, suspense, and a "
            "narrator whose account cannot be fully trusted."
        ),
    ),
    GoldenRag(
        question="a coming-of-age story about friendship and growing up",
        reference=(
            "A coming-of-age novel centered on adolescence, friendship, and "
            "self-discovery."
        ),
    ),
    GoldenRag(
        question="sweeping historical fiction set during wartime",
        reference=(
            "Historical fiction set against a major war, following characters "
            "through its upheaval."
        ),
    ),
    GoldenRag(
        question="a gripping murder mystery with a clever detective",
        reference=(
            "A mystery or detective novel driven by a murder investigation and "
            "an astute investigator."
        ),
    ),
    GoldenRag(
        question="a witty, light-hearted romance",
        reference=(
            "A humorous, feel-good romance with charming characters and a "
            "light tone."
        ),
    ),
    GoldenRag(
        question="epic high fantasy with intricate world-building",
        reference=(
            "An epic fantasy with a richly imagined world, magic, and a "
            "large-scale quest or conflict."
        ),
    ),
    # --- hybrid / structured (exercise the SQL filter too) ---
    GoldenRag(
        question="90s sci-fi with a strong female lead",
        reference=(
            "Science-fiction novels published in the 1990s featuring a "
            "prominent, capable female protagonist."
        ),
    ),
    GoldenRag(
        question="highly-rated popular-science books about the universe",
        reference=(
            "Well-rated non-fiction about astronomy, physics, or cosmology that "
            "explains the universe for a general audience."
        ),
    ),
]
