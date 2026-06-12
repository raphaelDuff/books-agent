# State

The state schema is the contract every node reads from and writes to. Get it right
first; everything else follows from it.

## TypedDict vs Pydantic

Use **TypedDict** by default — it is the lightest and what most LangGraph code expects.
Reach for a **Pydantic `BaseModel`** as the state only when you need validation/coercion
of the state itself on every update (rare). Pydantic is almost always the right choice for
node _outputs_ (structured output) — that is separate from the graph state, see
`nodes_and_di.md`.

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class BooksAgentState(TypedDict):
    question: str                                  # input, set once
    intent: str                                    # "STRUCTURED" | "SEMANTIC" | "HYBRID"
    filters: dict                                  # structured filters extracted by router
    semantic_query: str                            # rewritten query for vector search
    sql_results: list[dict]                        # rows from DuckDB
    semantic_results: list[dict]                   # hits from Weaviate
    answer: str                                    # final recommendation text
```

## Reducers: the single most common bug

By default, when a node returns a value for a key, it **overwrites** the previous value.
That is correct for scalar fields like `intent` or `answer`. It is _wrong_ for any key
that should **accumulate** across nodes — the classic case being a running message list,
or results gathered by several parallel nodes into the same key.

To accumulate, annotate the key with a **reducer**: a function `(current, update) -> merged`.

```python
import operator
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]   # appends, dedupes by id
    log: Annotated[list[str], operator.add]               # concatenates lists
    score: float                                          # plain key -> overwrites
```

Rule of thumb: **if two nodes (especially parallel ones) write the same key, that key
needs a reducer**, or one write will clobber the other. In books-agent we sidestep this
by having the parallel SQL and semantic nodes write to _different_ keys
(`sql_results` / `semantic_results`) and merging them in a dedicated node. That is often
cleaner than a shared reducer — prefer separate keys when the merge logic is non-trivial.

## Partial updates — never mutate

A node returns a dict containing **only the keys it changed**. LangGraph applies that
partial update (via the reducer or overwrite) to produce the next state. Do not mutate the
incoming `state` object; treat it as read-only.

```python
# GOOD — return only what changed
def classify_intent(state: BooksAgentState, config) -> dict:
    result = ...  # call LLM
    return {"intent": result.intent, "filters": result.filters,
            "semantic_query": result.semantic_query}

# BAD — mutating state in place; reducers won't run, parallel writes corrupt
def classify_intent(state, config):
    state["intent"] = "HYBRID"   # don't
    return state                 # don't return the whole state
```

## Separate Input / Output schemas (optional but tidy)

The internal state often carries scratch fields the caller should neither supply nor see.
You can declare narrower input and output schemas so the public interface is clean:

```python
class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str
    sql_results: list[dict]
    semantic_results: list[dict]

builder = StateGraph(BooksAgentState, input=InputState, output=OutputState)
```

Now `agent.invoke({"question": "..."})` is the only valid input shape, and the result
exposes only `answer` + results — not the intermediate `intent`/`filters` scratch.

## Checkpointer-safety

If you compile with a checkpointer, everything in state gets serialized. Keep state
**serializable** — store ids, dicts, and primitives, not live DB connections or client
objects. Those belong in config (see `nodes_and_di.md`), never in state.
