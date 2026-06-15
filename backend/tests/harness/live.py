"""Live-eval helpers: drive the REAL graph and score it with Ragas.

Only used by the opt-in :mod:`tests.test_live_eval` layer (``RUN_LIVE_EVAL=1``).
Everything here makes real network calls (OpenAI + Postgres + Weaviate), so it
must never run in the default hermetic suite.

The graph is wired exactly as the FastAPI lifespan does
([app/infra/web/app.py]) — the same adapters, so we measure the production path.
Ragas uses its modern ``ragas.metrics.collections`` API (plain ``ascore`` over
strings), with an OpenAI judge built via ``llm_factory`` / ``OpenAIEmbeddings``.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlparse

import weaviate

from app.agent.graph import build_graph
from app.domain.entities.book import BookDomain
from app.infra.agent_settings import AgentSettings
from app.infra.config import Config
from app.infra.embeddings.openai_embeddings import OpenAIEmbeddingsService
from app.infra.llm.openai_llm import OpenAILLMService
from app.infra.persistence.book_repository import BookPostgreRepository
from app.infra.vector.weaviate_repository import WeaviateBookRepository

# Register the Ragas import shim before any ragas import happens elsewhere.
from tests.harness import _ragas_compat  # noqa: F401


def _connect_weaviate(url: str):
    parsed = urlparse(url)
    return weaviate.connect_to_local(
        host=parsed.hostname or "localhost", port=parsed.port or 8080
    )


async def run_real_graph(question: str) -> dict[str, Any]:
    """Run the real compiled graph end-to-end; return the full final state.

    Returns the full ``BooksAgentState`` (including ``sql_results`` /
    ``semantic_results``), not just the trimmed ``OutputState``, so we can build
    Ragas ``retrieved_contexts``.
    """
    settings = AgentSettings()  # type: ignore[call-arg]
    llm = OpenAILLMService(
        model=settings.openai_chat_model, api_key=settings.openai_api_key
    )
    embeddings = OpenAIEmbeddingsService(
        model=settings.openai_embedding_model, api_key=settings.openai_api_key
    )
    client = _connect_weaviate(settings.weaviate_url)
    try:
        vector_repo = WeaviateBookRepository(client, settings.weaviate_collection)
        session_factory = Config.get_session_factory()
        graph = build_graph()
        async with session_factory() as session:
            book_repo = BookPostgreRepository(session)
            config = {
                "configurable": {
                    "thread_id": f"live::{question}",
                    "llm": llm,
                    "embeddings": embeddings,
                    "vector_repo": vector_repo,
                    "book_repo": book_repo,
                }
            }
            await graph.ainvoke({"question": question}, config=config)
            snapshot = await graph.aget_state(config)
            return dict(snapshot.values)
    finally:
        client.close()
        await Config.dispose_engine()


def build_contexts_and_response(state: dict[str, Any]) -> tuple[list[str], str]:
    """Turn final graph state into Ragas ``retrieved_contexts`` + ``response``.

    Contexts = the candidate books the reranker saw (semantic then SQL, deduped
    by isbn13). Response = the ranked picks rendered as ``title — justification``.
    """
    ordered = list(state.get("semantic_results") or []) + list(
        state.get("sql_results") or []
    )
    seen: set[str] = set()
    contexts: list[str] = []
    for data in ordered:
        isbn = data.get("isbn13")
        if isbn and isbn not in seen:
            seen.add(isbn)
            book = BookDomain.from_dict(data)
            contexts.append(f"{book.title} by {book.authors}: {book.description}")

    picks = state.get("picks") or []
    response = "\n".join(
        f"{p['book']['title']} — {p['justification']}" for p in picks
    ) or "(no recommendations)"
    return contexts, response


def _is_reasoning_model(model: str) -> bool:
    """GPT-5+/o-series need ``max_completion_tokens`` (not ``max_tokens``).

    Ragas has its own detector but it does ``int("5.4")`` on a dotted minor
    version like ``gpt-5.4-mini-2026-03-17`` and silently fails, so it leaves the
    unsupported ``max_tokens`` in place. We parse only the leading major digits.
    """
    m = model.lower()
    if re.match(r"o[1-9]([-_]|$)", m):
        return True
    gpt = re.match(r"gpt-(\d+)", m)  # leading digits before any '.' or '-'
    return bool(gpt and int(gpt.group(1)) >= 5) or m == "codex-mini"


def _build_judge():
    """OpenAI-backed Ragas judge LLM + embeddings (modern collections API)."""
    from openai import AsyncOpenAI
    from ragas.embeddings import OpenAIEmbeddings as RagasOpenAIEmbeddings
    from ragas.llms import llm_factory

    settings = AgentSettings()  # type: ignore[call-arg]
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    judge_model = os.getenv("RAGAS_JUDGE_MODEL", settings.openai_chat_model)
    judge = llm_factory(judge_model, client=client)

    # Work around Ragas mis-detecting dotted-version reasoning models: remap the
    # request args ourselves (drop max_tokens/top_p, bump completion budget so
    # GPT-5 structured output isn't truncated, pin temperature to the only value
    # these models accept).
    if _is_reasoning_model(judge_model):
        args = judge.model_args
        budget = args.pop("max_tokens", 1024)
        args["max_completion_tokens"] = max(budget, 4096)
        args.pop("top_p", None)
        args["temperature"] = 1.0

    emb = RagasOpenAIEmbeddings(client=client, model=settings.openai_embedding_model)
    return judge, emb


async def score_with_ragas(
    question: str,
    response: str,
    retrieved_contexts: list[str],
    reference: str,
) -> dict[str, float | None]:
    """Score one real recommendation with the four confirmed Ragas metrics."""
    from ragas.metrics.collections import (
        AnswerRelevancy,
        ContextPrecisionWithReference,
        ContextRecall,
        Faithfulness,
    )

    judge, emb = _build_judge()

    faithfulness = await Faithfulness(llm=judge).ascore(
        user_input=question,
        response=response,
        retrieved_contexts=retrieved_contexts,
    )
    relevancy = await AnswerRelevancy(llm=judge, embeddings=emb).ascore(
        user_input=question, response=response
    )
    precision = await ContextPrecisionWithReference(llm=judge).ascore(
        user_input=question,
        reference=reference,
        retrieved_contexts=retrieved_contexts,
    )
    recall = await ContextRecall(llm=judge).ascore(
        user_input=question,
        retrieved_contexts=retrieved_contexts,
        reference=reference,
    )
    return {
        "faithfulness": faithfulness.value,
        "answer_relevancy": relevancy.value,
        "context_precision": precision.value,
        "context_recall": recall.value,
    }
