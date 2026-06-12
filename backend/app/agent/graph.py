from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent.config import ConfigSchema
from app.agent.nodes import (
    classify_intent,
    rank,
    repair_sql,
    semantic_search,
    sql_search,
)
from app.agent.routing import route_after_classify, route_after_sql
from app.agent.state import BooksAgentState, InputState, OutputState


def build_graph():
    """Build and compile the books recommendation graph.

    Compiled WITH a ``MemorySaver`` so state persists per ``thread_id`` (plan:
    conversation-memory plumbing). Dependencies are not bound here — they flow
    in through ``RunnableConfig`` at invoke time.
    """
    builder = StateGraph(
        BooksAgentState,
        input=InputState,
        output=OutputState,
        config_schema=ConfigSchema,
    )

    builder.add_node("classify_intent", classify_intent)
    builder.add_node("sql_search", sql_search)
    builder.add_node("repair_sql", repair_sql)
    builder.add_node("semantic_search", semantic_search)
    builder.add_node("rank", rank)

    builder.add_edge(START, "classify_intent")
    builder.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {"sql_search": "sql_search", "semantic_search": "semantic_search"},
    )
    builder.add_conditional_edges(
        "sql_search",
        route_after_sql,
        {
            "repair_sql": "repair_sql",
            "semantic_search": "semantic_search",
            "rank": "rank",
        },
    )
    builder.add_edge("repair_sql", "sql_search")
    builder.add_edge("semantic_search", "rank")
    builder.add_edge("rank", END)

    return builder.compile(checkpointer=MemorySaver())
