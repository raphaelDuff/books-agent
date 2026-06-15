"""Live evaluation — real models, real DBs, Ragas RAG-quality metrics.

RUNS BY DEFAULT. Requires a configured ``OPENAI_API_KEY`` and running Postgres +
Weaviate (see the README "Running the project"). When no API key is available
(e.g. CI without secrets) these tests skip cleanly instead of failing; set
``SKIP_LIVE_EVAL=1`` to opt out explicitly, or run only the hermetic suite with
``uv run pytest -m "not live"``.

    uv run pytest -m live -s          # just the live layer, with printed scores

Two layers:
1. Deterministic intent-classification accuracy (no judge — a label compare).
2. Ragas RAG-quality scoring of the real end-to-end graph (LLM judge).

These complement the hermetic harness in ``test_harness.py`` (graph mechanics);
here we measure *real model quality*, which is non-deterministic by nature, so
the gates are deliberately lenient — the value is the printed scores.
"""

import os

import pytest

from tests.harness.golden_dataset import GOLDEN_INTENTS, GOLDEN_RAG


def _live_prereqs() -> tuple[bool, str]:
    """Whether the live layer can run. Skips (not fails) on missing config."""
    if os.getenv("SKIP_LIVE_EVAL"):
        return False, "SKIP_LIVE_EVAL is set"
    try:
        from app.infra.agent_settings import AgentSettings

        AgentSettings()  # type: ignore[call-arg]  # raises if OPENAI_API_KEY absent
    except Exception as exc:  # noqa: BLE001 - any config failure -> skip
        return False, f"live prerequisites unavailable ({type(exc).__name__})"
    return True, ""


_LIVE_OK, _LIVE_REASON = _live_prereqs()

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not _LIVE_OK, reason=_LIVE_REASON),
]


async def test_intent_classification_accuracy():
    """Real router accuracy over the golden intent labels + confusion matrix."""
    from app.infra.agent_settings import AgentSettings
    from app.infra.llm.openai_llm import OpenAILLMService

    settings = AgentSettings()  # type: ignore[call-arg]
    llm = OpenAILLMService(
        model=settings.openai_chat_model, api_key=settings.openai_api_key
    )

    correct = 0
    confusion: dict[tuple[str, str], int] = {}
    for gold in GOLDEN_INTENTS:
        decision = await llm.classify(gold.question)
        got = decision.intent
        key = (gold.expected_intent.value, got.value)
        confusion[key] = confusion.get(key, 0) + 1
        if got == gold.expected_intent:
            correct += 1

    accuracy = correct / len(GOLDEN_INTENTS)
    print(f"\nIntent accuracy: {correct}/{len(GOLDEN_INTENTS)} = {accuracy:.0%}")
    print("Confusion (expected -> got):")
    for (expected, got), n in sorted(confusion.items()):
        mark = "" if expected == got else "  <-- miss"
        print(f"  {expected:>10} -> {got:<10} : {n}{mark}")

    # lenient gate: the real model should get a clear majority right
    assert accuracy >= 0.6, f"intent accuracy {accuracy:.0%} below 60%"


@pytest.mark.parametrize("gold", GOLDEN_RAG, ids=lambda g: g.question[:32])
async def test_ragas_rag_quality(gold):
    """Score one real recommendation with the four confirmed Ragas metrics."""
    from tests.harness.live import (
        build_contexts_and_response,
        run_real_graph,
        score_with_ragas,
    )

    state = await run_real_graph(gold.question)
    contexts, response = build_contexts_and_response(state)

    assert contexts, "no contexts retrieved — is the data loaded / Weaviate up?"

    scores = await score_with_ragas(
        question=gold.question,
        response=response,
        retrieved_contexts=contexts,
        reference=gold.reference,
    )

    print(f"\nQ: {gold.question}")
    print(f"  intent={state.get('intent')} picks={len(state.get('picks') or [])}")
    for name, value in scores.items():
        shown = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
        print(f"  {name:>18}: {shown}")

    # sanity gate only — the printed scores are the real deliverable
    assert any(v is not None for v in scores.values()), "all Ragas scores are None"
