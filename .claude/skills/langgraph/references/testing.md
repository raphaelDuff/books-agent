# Testing

The payoff of the node + port design is that you can test the interesting logic without a
network, an LLM, or a database. Three levels:

## 1. Test a node in isolation (the high-value test)

Call the node function directly with a hand-built state and a config carrying **fake
ports**. Assert on the partial dict it returns. No graph, no I/O.

```python
from books_agent.nodes import classify_intent

class FakeLLM:
    def classify(self, question: str):
        from books_agent.domain.ports import IntentClassification
        return IntentClassification(intent="HYBRID",
                                    filters={"published_year_gte": 1990,
                                             "published_year_lte": 1999},
                                    semantic_query="car chase pursuit thriller",
                                    reasoning="decade + theme")

def test_classify_intent_extracts_year_and_theme():
    state = {"question": "books from the 90s about car chases"}
    out = classify_intent(state, config={"configurable": {"llm": FakeLLM()}})
    assert out["intent"] == "HYBRID"
    assert out["filters"]["published_year_gte"] == 1990
    assert "chase" in out["semantic_query"]
```

This is the test that catches real regressions: prompt changes, schema drift, mapping of
LLM output into state.

## 2. Test the router

Routers are pure functions of state — the easiest thing to test exhaustively. Cover every
branch, including the parallel one.

```python
from books_agent.routing import route_by_intent

def test_router_branches():
    assert route_by_intent({"intent": "STRUCTURED"}) == "sql_search"
    assert route_by_intent({"intent": "SEMANTIC"}) == "semantic_search"
    assert route_by_intent({"intent": "HYBRID"}) == ["sql_search", "semantic_search"]
```

If you add an intent later and forget to extend the mapping, a test like this fails before
the graph does.

## 3. Test the compiled graph end-to-end (with fakes)

Build the graph, inject fake ports via config, invoke it on a question, assert on the
output shape. Use an in-memory checkpointer if your graph needs one.

```python
from langgraph.checkpoint.memory import MemorySaver
from books_agent.agent import build_graph   # a builder fn that returns the uncompiled graph

def test_hybrid_path_merges_results():
    graph = build_graph().compile(checkpointer=MemorySaver())
    out = graph.invoke(
        {"question": "90s books about car chases"},
        config={"configurable": {"llm": FakeLLM(),
                                  "sql": FakeSql(rows=[{"isbn": "1"}]),
                                  "book_search": FakeSearch(hits=[{"isbn": "1"}, {"isbn": "2"}]),
                                  "thread_id": "test"}},
    )
    assert out["answer"]
    assert {"isbn": "1"} in out["sql_results"]
```

Expose a `build_graph()` function (returns the uncompiled `StateGraph`) in addition to the
compiled `agent` export — it makes tests able to compile with a test checkpointer while
`agent.py` compiles the production one. See the `agent.py` template.

## Observability in tests and beyond

Enable LangSmith tracing with env vars (`LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=...`)
and the whole graph run is captured automatically — every node, the structured-output call,
the branch taken. Name runs and add metadata via config (`{"run_name": "...", "tags": [...],
"metadata": {...}}`) so traces are searchable. The `reasoning` field on
`IntentClassification` shows up in the trace, which makes misclassification bugs obvious.
