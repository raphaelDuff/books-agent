from typing import Any, TypedDict


class InputState(TypedDict):
    question: str


class OutputState(TypedDict):
    intent: str
    generated_sql: str | None
    picks: list[dict[str, Any]]


class BooksAgentState(TypedDict, total=False):
    """Graph state. All values are plain JSON-serializable data (dicts/primitives,
    no domain objects or clients) so the checkpointer can round-trip them;
    injected dependencies live in ``RunnableConfig`` instead.

    Books are carried as plain dicts (``BookDomain.to_dict()``) — the msgpack
    checkpointer cannot reconstruct domain dataclasses and would silently turn
    them into ``None``. The graph is sequential per intent, so no key is written
    by two nodes at once — no reducers are needed.
    """

    # input
    question: str

    # classify_intent
    intent: str
    semantic_query: str
    sql: str | None

    # sql_search / repair_sql — book payload dicts
    sql_results: list[dict[str, Any]]
    sql_allowlist: list[str]
    generated_sql: str | None
    sql_error: str | None
    sql_attempts: int

    # semantic_search — book payload dicts
    semantic_results: list[dict[str, Any]]

    # rank — each: {"book": <book dict>, "justification": str}
    picks: list[dict[str, Any]]
