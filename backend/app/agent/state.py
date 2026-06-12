from typing import TypedDict

from app.application.service_ports.llm_service import RankedPick
from app.domain.entities.book import BookDomain


class InputState(TypedDict):
    question: str


class OutputState(TypedDict):
    intent: str
    generated_sql: str | None
    picks: list[RankedPick]


class BooksAgentState(TypedDict, total=False):
    """Graph state. All values are plain data (no clients) so the checkpointer
    can serialize them; injected dependencies live in ``RunnableConfig`` instead.

    The graph is sequential per intent, so no key is written by two nodes at
    once — no reducers are needed.
    """

    # input
    question: str

    # classify_intent
    intent: str
    semantic_query: str
    sql: str | None

    # sql_search / repair_sql
    sql_results: list[BookDomain]
    sql_allowlist: list[str]
    generated_sql: str | None
    sql_error: str | None
    sql_attempts: int

    # semantic_search
    semantic_results: list[BookDomain]

    # rank
    picks: list[RankedPick]
