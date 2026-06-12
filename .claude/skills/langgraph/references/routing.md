# Routing & Conditional Edges

This is where the books-agent design earns its keep: one router node decides whether a
request needs a structured filter, a semantic search, or **both in parallel**.

## Static edges vs conditional edges

- `add_edge(a, b)` — always go from `a` to `b`.
- `add_conditional_edges(source, route_fn, mapping)` — call `route_fn(state)`, take its
  return value, look it up in `mapping`, and route to that node (or those nodes).

`START` and `END` are the entry/exit sentinels: `from langgraph.graph import START, END`.

## The router function

The router is a **separate function from the node that produced the decision**. The
`classify_intent` node writes `intent` into state; the router just reads it and returns a
key. Keep routing logic dumb — all the intelligence (the LLM call) already happened in the
node.

```python
def route_by_intent(state: BooksAgentState) -> str | list[str]:
    intent = state["intent"]
    if intent == "STRUCTURED":
        return "sql_search"
    if intent == "SEMANTIC":
        return "semantic_search"
    return ["sql_search", "semantic_search"]   # HYBRID -> run both in parallel
```

## The mapping pitfall

The value `route_fn` returns must be a **key in the mapping dict** (or, when returning a
list, every element must be). A typo or an unhandled branch routes nowhere and the graph
fails — often confusingly. Always make the mapping exhaustive over the router's possible
returns.

```python
builder.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "sql_search": "sql_search",
        "semantic_search": "semantic_search",
    },
)
```

Note: when `route_fn` returns a **list of node names**, you do not list the list in the
mapping — you list each individual node name. The list itself triggers parallel fan-out to
those nodes.

## Parallel fan-out and fan-in (the HYBRID path)

Returning `["sql_search", "semantic_search"]` makes LangGraph run both nodes in the same
super-step, concurrently. They must not write the same state key (or that key needs a
reducer — see `state.md`). In books-agent they write `sql_results` and `semantic_results`
respectively, so there is no conflict.

Both nodes then point to a single `merge` node (fan-in). `merge` runs **once**, after both
upstream nodes finish, and combines whatever is present:

```python
builder.add_node("sql_search", sql_search)
builder.add_node("semantic_search", semantic_search)
builder.add_node("merge", merge_results)
builder.add_node("rank", rank_and_answer)

builder.add_edge(START, "classify_intent")
builder.add_conditional_edges("classify_intent", route_by_intent,
                              {"sql_search": "sql_search",
                               "semantic_search": "semantic_search"})
builder.add_edge("sql_search", "merge")
builder.add_edge("semantic_search", "merge")
builder.add_edge("merge", "rank")
builder.add_edge("rank", END)
```

Because both search nodes feed `merge`, the **STRUCTURED-only** and **SEMANTIC-only** paths
also pass through `merge` cleanly — the absent side is just an empty list. `merge_results`
should handle "one side empty" gracefully (intersect when both present, otherwise pass the
non-empty side through). This single graph shape covers all three intents without special
casing.

### Send (advanced map-reduce)

When you need to fan out over a _dynamic_ number of branches (e.g. one search per extracted
sub-query), use `Send` instead of a static list:

```python
from langgraph.types import Send

def route_by_intent(state) -> list[Send]:
    return [Send("semantic_search", {"semantic_query": q}) for q in state["subqueries"]]
```

For books-agent the fixed two-way fan-out above is enough; reach for `Send` only when the
branch count depends on the data.
