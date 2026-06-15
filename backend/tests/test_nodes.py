from typing import Sequence

from app.agent.nodes import (
    classify_intent,
    rank,
    repair_sql,
    semantic_search,
    sql_search,
)
from app.agent.routing import route_after_classify, route_after_sql
from app.application.service_ports.llm_service import IntentClassification, RankedPick
from app.domain.entities.book import BookDomain
from app.domain.value_objects import Intent


def make_book(isbn: str, title: str = "T") -> BookDomain:
    return BookDomain(isbn13=isbn, title=title, authors="A", description="D")


class FakeLLM:
    def __init__(self, classification: IntentClassification | None = None) -> None:
        self._classification = classification or IntentClassification(
            intent=Intent.HYBRID, semantic_query="mood", sql="SELECT * FROM books"
        )

    async def classify(self, question: str) -> IntentClassification:
        return self._classification

    async def repair_sql(self, sql: str, error: str) -> str:
        return "SELECT * FROM books WHERE published_year = 1999"

    async def rank_and_justify(
        self, question: str, candidates: Sequence[BookDomain], limit: int
    ) -> list[RankedPick]:
        return [RankedPick(book=b, justification="because") for b in candidates[:limit]]


class FakeBookRepo:
    def __init__(self, books=None, error: Exception | None = None) -> None:
        self._books = books or []
        self._error = error

    async def execute_select(self, sql: str) -> Sequence[BookDomain]:
        if self._error:
            raise self._error
        return self._books


class FakeVectorRepo:
    def __init__(self, books=None) -> None:
        self._books = books or []
        self.last_allowlist = "unset"

    async def search_by_vector(self, vector, limit, isbn13_allowlist=None):
        self.last_allowlist = isbn13_allowlist
        return self._books


class FakeEmbeddings:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


def cfg(**deps):
    return {"configurable": deps}


# --- classify_intent ---

async def test_classify_intent_maps_decision_into_state():
    decision = IntentClassification(
        intent=Intent.STRUCTURED, semantic_query="", sql="SELECT * FROM books"
    )
    out = await classify_intent({"question": "q"}, cfg(llm=FakeLLM(decision)))
    assert out["intent"] == "STRUCTURED"
    assert out["sql"] == "SELECT * FROM books"
    assert out["sql_attempts"] == 0


# --- sql_search ---

async def test_sql_search_success_builds_allowlist():
    repo = FakeBookRepo(books=[make_book("111"), make_book("222")])
    out = await sql_search(
        {"sql": "SELECT * FROM books", "sql_attempts": 0}, cfg(book_repo=repo)
    )
    assert out["sql_allowlist"] == ["111", "222"]
    assert out["sql_error"] is None
    assert out["sql_attempts"] == 1
    assert out["generated_sql"] == "SELECT * FROM books"


async def test_sql_search_captures_error_and_increments_attempts():
    repo = FakeBookRepo(error=ValueError("boom"))
    out = await sql_search(
        {"sql": "BAD", "sql_attempts": 0}, cfg(book_repo=repo)
    )
    assert out["sql_results"] == []
    assert "boom" in out["sql_error"]
    assert out["sql_attempts"] == 1


# --- repair_sql ---

async def test_repair_sql_replaces_sql():
    out = await repair_sql({"sql": "BAD", "sql_error": "syntax"}, cfg(llm=FakeLLM()))
    assert out["sql"].lower().startswith("select")


# --- semantic_search ---

async def test_semantic_search_passes_allowlist_on_hybrid():
    vec = FakeVectorRepo(books=[make_book("111")])
    state = {
        "question": "q",
        "semantic_query": "mood",
        "intent": Intent.HYBRID.value,
        "sql_allowlist": ["111", "222"],
    }
    await semantic_search(state, cfg(embeddings=FakeEmbeddings(), vector_repo=vec))
    assert vec.last_allowlist == ["111", "222"]


async def test_semantic_search_no_allowlist_on_pure_semantic():
    vec = FakeVectorRepo(books=[make_book("111")])
    state = {
        "question": "q",
        "semantic_query": "mood",
        "intent": Intent.SEMANTIC.value,
        "sql_allowlist": ["111"],
    }
    await semantic_search(state, cfg(embeddings=FakeEmbeddings(), vector_repo=vec))
    assert vec.last_allowlist is None


# --- rank ---

async def test_rank_dedupes_candidates_by_isbn():
    state = {
        "question": "q",
        "semantic_results": [make_book("111").to_dict(), make_book("222").to_dict()],
        "sql_results": [make_book("222").to_dict(), make_book("333").to_dict()],
    }
    out = await rank(state, cfg(llm=FakeLLM()))
    isbns = [p["book"]["isbn13"] for p in out["picks"]]
    assert isbns == ["111", "222", "333"]


# --- routing ---

def test_book_dicts_survive_checkpoint_serialization():
    # Regression: BookDomain dataclasses round-tripped to None through the
    # msgpack checkpointer; state must hold plain dicts instead.
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

    serde = JsonPlusSerializer()
    state = {
        "sql_results": [make_book("111", "T1").to_dict()],
        "picks": [{"book": make_book("222", "T2").to_dict(), "justification": "why"}],
    }
    restored = serde.loads_typed(serde.dumps_typed(state))
    assert restored["sql_results"][0]["isbn13"] == "111"
    assert restored["picks"][0]["book"]["title"] == "T2"
    assert BookDomain.from_dict(restored["picks"][0]["book"]).isbn13 == "222"


def test_route_after_classify():
    assert route_after_classify({"intent": "SEMANTIC"}) == "semantic_search"
    assert route_after_classify({"intent": "STRUCTURED"}) == "sql_search"
    assert route_after_classify({"intent": "HYBRID"}) == "sql_search"


def test_route_after_sql_repairs_once_then_proceeds():
    # error + attempts < max -> repair
    assert (
        route_after_sql({"sql_error": "x", "sql_attempts": 1, "intent": "STRUCTURED"})
        == "repair_sql"
    )
    # error but attempts exhausted -> proceed (no infinite loop)
    assert (
        route_after_sql({"sql_error": "x", "sql_attempts": 2, "intent": "STRUCTURED"})
        == "rank"
    )
    # success on HYBRID -> semantic
    assert (
        route_after_sql({"sql_error": None, "sql_attempts": 1, "intent": "HYBRID"})
        == "semantic_search"
    )
    # success on STRUCTURED -> rank
    assert (
        route_after_sql({"sql_error": None, "sql_attempts": 1, "intent": "STRUCTURED"})
        == "rank"
    )
