---
name: langgraph-agent
description: "Build, extend, or debug Python LangGraph agents with clean, production-grade conventions (state and reducers, node functions, dependency injection, structured output, conditional-edge routing, the langgraph.json deploy contract). Use whenever working with a StateGraph, graph state, nodes, a router/classify node, conditional edges, or langgraph.json — any LangGraph agent that branches between tools or data sources. Not for plain LangChain (LCEL) chains with no graph."
---

# Building LangGraph Agents

This skill encodes the conventions that keep a LangGraph project maintainable and
deployable. The folder layout is the easy part; the value here is in the patterns
that are easy to get subtly wrong (reducers, state mutation, conditional-edge
mappings, dependency injection, the checkpointer/deploy nuance).

The running example throughout is **books-agent**: a book recommender that routes
a natural-language request to a structured SQL filter (PostgreSQL), a semantic search
(Weaviate), or both in sequence, then ranks and justifies the results.

## Mental model

A LangGraph app is three things stacked:

1. **The deploy contract** — `langgraph.json` points `graphs` at a `file.py:variable`,
   where the variable is a compiled graph (or a function that builds one). This is the
   only non-negotiable part of the structure.
2. **The orchestration** — the `StateGraph`: state schema, nodes, edges. This is where
   LangGraph-specific rules live.
3. **The domain** — business logic and I/O (the LLM client, the SQL engine, the vector
   store) live _outside_ the graph, behind interfaces (ports). Nodes are thin adapters
   that call into the domain. The graph package depends on the domain, never the reverse.

Keeping (3) separate from (2) is what makes nodes testable and the LLM vendor swappable.
Do not instantiate clients (`ChatOpenAI()`, a DB connection, a Weaviate client) at module
top level inside node files — inject them. See `references/nodes_and_di.md`.

## Folder structure

Start from this layout. The `my_agent/` package name and `agent.py` graph export are
what `langgraph.json` references.

```
books-agent/
├── books_agent/
│   ├── __init__.py
│   ├── agent.py            # builds + compiles the graph; exports `agent`
│   ├── state.py            # State schema (+ Input/Output schemas, reducers)
│   ├── nodes.py            # node functions: (state, config) -> dict
│   ├── routing.py          # conditional-edge router functions
│   ├── config.py           # ConfigSchema + dependency wiring
│   └── domain/             # ports + implementations (no LangGraph imports here)
│       ├── __init__.py
│       ├── ports.py        # Protocol/ABC interfaces: LLMPort, SearchPort...
│       └── adapters.py     # PostgreSQL, Weaviate, LLM implementations
├── tests/
│   └── test_nodes.py
├── .env
├── langgraph.json
└── pyproject.toml
```

## Workflow when scaffolding a new graph

1. **Define the state first** (`state.py`). The state shape drives everything else.
   Decide each key's type and whether it needs a reducer. → `references/state.md`
2. **Declare the ports** (`domain/ports.py`) for every external dependency a node
   will touch. Nodes depend on these, not on concrete clients.
3. **Write nodes as pure functions** that take `(state, config)`, read deps from
   config, and return a _partial_ dict of changed keys. → `references/nodes_and_di.md`
4. **Wire routing** with conditional edges and an explicit mapping. → `references/routing.md`
5. **Build and compile** the graph in `agent.py`, export the compiled `agent`.
6. **Write `langgraph.json`** pointing at it. → `assets/templates/langgraph.json`
7. **Add node-level tests** (mock the ports). → `references/testing.md`

Copy the starting points from `assets/templates/` rather than writing from scratch.

## Reference files — read the relevant one before writing that part

- `references/state.md` — TypedDict vs Pydantic, `Annotated` reducers, partial updates,
  separate Input/Output schemas. **Read before defining or changing state.**
- `references/nodes_and_di.md` — node signature, `RunnableConfig` vs `functools.partial`
  injection, structured output with Pydantic, sync vs async. **Read before writing nodes.**
- `references/routing.md` — conditional edges, the mapping pitfall, parallel fan-out for
  the HYBRID case, fan-in/merge. **Read before wiring branches.**
- `references/testing.md` — testing nodes in isolation, routers, and the compiled graph.
- `references/pitfalls.md` — the short list of mistakes that break graphs silently.
  **Skim this every time; it is the highest-value file.**

## Non-negotiable rules (the rest of the references explain why)

- Nodes return a **partial dict**, never mutate `state` in place.
- Any state key that _accumulates_ across nodes needs a **reducer** in its `Annotated` type.
- A conditional-edge router's return value **must** be a key in the mapping dict.
- External clients are **injected**, never created at import time inside node modules.
- When deploying to LangGraph Platform, compile **without** a checkpointer (the platform
  provides persistence). Pass `MemorySaver`/a real saver only for local/embedded use.
