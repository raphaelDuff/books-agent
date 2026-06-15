"""Graph nodes.

Each node is a thin async adapter: it pulls a dependency (a port) from
``config['configurable']``, calls it, and returns a *partial* state update. No
business logic, raw I/O, or LangChain types live here — that is what keeps nodes
unit-testable with mocked ports.
"""

from langchain_core.runnables import RunnableConfig

from app.agent.config import FINAL_PICKS, SEMANTIC_OVERFETCH
from app.agent.state import BooksAgentState
from app.application.repositories.book_repository import BookRepository
from app.application.repositories.book_vector_repository import BookVectorRepository
from app.application.service_ports.embeddings_service import EmbeddingsService
from app.application.service_ports.llm_service import LLMService
from app.domain.entities.book import BookDomain
from app.domain.value_objects import Intent

MAX_SQL_ATTEMPTS = 2  # initial attempt + one repair


def _deps(config: RunnableConfig) -> dict:
    """Injected dependencies from config. ``configurable`` is optional on
    RunnableConfig per the type stubs, so read it defensively."""
    return config.get("configurable") or {}


async def classify_intent(state: BooksAgentState, config: RunnableConfig) -> dict:
    llm: LLMService = _deps(config)["llm"]
    decision = await llm.classify(state["question"])
    return {
        "intent": decision.intent.value,
        "semantic_query": decision.semantic_query,
        "sql": decision.sql,
        "sql_attempts": 0,
    }


async def sql_search(state: BooksAgentState, config: RunnableConfig) -> dict:
    book_repo: BookRepository = _deps(config)["book_repo"]
    sql = state.get("sql") or ""
    attempts = state.get("sql_attempts", 0) + 1
    try:
        books = list(await book_repo.execute_select(sql))
        return {
            "sql_results": [b.to_dict() for b in books],
            "sql_allowlist": [b.isbn13 for b in books],
            "generated_sql": sql,
            "sql_error": None,
            "sql_attempts": attempts,
        }
    except Exception as exc:  # guard rejection or DB error → eligible for one repair
        return {
            "sql_results": [],
            "sql_allowlist": [],
            "generated_sql": sql,
            "sql_error": str(exc),
            "sql_attempts": attempts,
        }


async def repair_sql(state: BooksAgentState, config: RunnableConfig) -> dict:
    llm: LLMService = _deps(config)["llm"]
    fixed = await llm.repair_sql(state.get("sql") or "", state.get("sql_error") or "")
    return {"sql": fixed}


async def semantic_search(state: BooksAgentState, config: RunnableConfig) -> dict:
    embeddings: EmbeddingsService = _deps(config)["embeddings"]
    vector_repo: BookVectorRepository = _deps(config)["vector_repo"]

    vector = await embeddings.embed(state.get("semantic_query") or state["question"])
    allowlist = (
        state.get("sql_allowlist")
        if state.get("intent") == Intent.HYBRID.value
        else None
    )
    books = list(
        await vector_repo.search_by_vector(
            vector, limit=SEMANTIC_OVERFETCH, isbn13_allowlist=allowlist
        )
    )
    return {"semantic_results": [b.to_dict() for b in books]}


async def rank(state: BooksAgentState, config: RunnableConfig) -> dict:
    llm: LLMService = _deps(config)["llm"]

    # Candidate set depends on the path: semantic ordering wins when present,
    # otherwise the SQL rows. Dedupe by isbn13, preserving order. State holds
    # plain dicts, so reconstruct domain entities for the reranker.
    ordered = list(state.get("semantic_results") or []) + list(
        state.get("sql_results") or []
    )
    seen: set[str] = set()
    candidates: list[BookDomain] = []
    for data in ordered:
        isbn = data.get("isbn13")
        if isbn and isbn not in seen:
            seen.add(isbn)
            candidates.append(BookDomain.from_dict(data))

    picks = await llm.rank_and_justify(state["question"], candidates, limit=FINAL_PICKS)
    return {
        "picks": [
            {"book": p.book.to_dict(), "justification": p.justification} for p in picks
        ]
    }
