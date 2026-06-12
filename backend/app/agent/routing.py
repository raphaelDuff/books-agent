"""Conditional-edge routers.

Routers are dumb: all the intelligence already happened in the nodes. They read
state and return a key that MUST exist in the edge mapping.
"""

from app.agent.nodes import MAX_SQL_ATTEMPTS
from app.agent.state import BooksAgentState
from app.domain.value_objects import Intent


def route_after_classify(state: BooksAgentState) -> str:
    """STRUCTURED/HYBRID run SQL first; SEMANTIC goes straight to vector search."""
    if state.get("intent") == Intent.SEMANTIC.value:
        return "semantic_search"
    return "sql_search"


def route_after_sql(state: BooksAgentState) -> str:
    """One repair attempt on failure; then SEMANTIC ranking for HYBRID, else rank."""
    if state.get("sql_error") and state.get("sql_attempts", 0) < MAX_SQL_ATTEMPTS:
        return "repair_sql"
    if state.get("intent") == Intent.HYBRID.value:
        return "semantic_search"
    return "rank"
