# Nodes & Dependency Injection

## Node signature

A node is a plain function from state to a partial state update. It may optionally take a
second `config` argument to read injected dependencies and runtime settings.

```python
from langchain_core.runnables import RunnableConfig

def node_name(state: BooksAgentState, config: RunnableConfig) -> dict:
    ...
    return {"changed_key": value}   # partial update only
```

Keep nodes **thin**: a node orchestrates, it does not contain business logic or raw I/O.
It pulls a dependency (a port) from config, calls it, and maps the result into state. The
actual SQL/HTTP/LLM work lives in the adapter behind the port. This is what makes nodes
unit-testable without a network.

## Dependency injection — two patterns, when to use each

Never do this inside a node module — it binds the graph to one vendor and runs at import:

```python
# BAD: module-level client
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")          # created on import, impossible to mock cleanly

def classify_intent(state):
    return llm.invoke(...)                 # hidden global dependency
```

### Pattern A — `RunnableConfig` (runtime injection, preferred)

Pass dependencies through `config["configurable"]`. The graph stays a pure description;
deps are supplied at invoke time (or wired once in `agent.py`). Best when you want to swap
implementations per environment (real vs fake) or per request.

```python
def classify_intent(state: BooksAgentState, config: RunnableConfig) -> dict:
    llm = config["configurable"]["llm"]            # an LLMPort implementation
    result = llm.classify(state["question"])
    return {"intent": result.intent, "filters": result.filters,
            "semantic_query": result.semantic_query}

# supplied at invoke:
agent.invoke({"question": q}, config={"configurable": {"llm": real_llm,
                                                       "book_search": weaviate_adapter,
                                                       "sql": postgres_adapter}})
```

Declare the shape with a config schema so it is documented and validated:

```python
class ConfigSchema(TypedDict):
    llm: LLMPort
    sql: SqlSearchPort
    book_search: SemanticSearchPort

builder = StateGraph(BooksAgentState, config_schema=ConfigSchema)
```

### Pattern B — `functools.partial` (construction-time wiring)

Bind dependencies when you build the graph. Best when deps are fixed for the lifetime of
the compiled graph and you do not need to vary them per request.

```python
from functools import partial

def classify_intent(state, *, llm: LLMPort) -> dict:
    result = llm.classify(state["question"])
    return {"intent": result.intent, ...}

builder.add_node("classify_intent", partial(classify_intent, llm=real_llm))
```

**Choosing:** use `RunnableConfig` when you want per-invoke swappability (and it is the
idiomatic path for LangGraph Platform, where config flows through). Use `partial` for
simple, fixed wiring in an embedded app. Both keep the node free of global clients; pick
one per project and stay consistent.

## Structured output

For any node that classifies or extracts (the router being the prime example), bind a
Pydantic schema to the model with `.with_structured_output(...)`. This guarantees a typed
object instead of free text you have to parse.

```python
from pydantic import BaseModel, Field
from typing import Literal

class IntentClassification(BaseModel):
    intent: Literal["STRUCTURED", "SEMANTIC", "HYBRID"]
    filters: dict = Field(default_factory=dict,
                          description="e.g. {'published_year_gte': 1990, 'published_year_lte': 1999}")
    semantic_query: str = Field(default="",
                                description="rewritten query for vector search; empty if STRUCTURED")
    reasoning: str = Field(description="why this intent — useful in LangSmith traces")

# inside the LLM adapter that implements LLMPort:
structured = self._chat_model.with_structured_output(IntentClassification)
result: IntentClassification = structured.invoke(prompt)
```

Put `with_structured_output` inside the **adapter**, so the node just calls
`llm.classify(...)` and gets back a typed object. The node never touches LangChain types.

## Sync vs async

Nodes can be `def` or `async def`. If a node does network I/O and you run the graph with
`ainvoke`/`astream`, make it `async def` and `await` the I/O — a blocking call inside an
async node stalls the whole event loop. Do not mix: a sync node that calls
`requests.get(...)` under an async graph is a classic latency bug. Keep the port's
interface honest about which it is (`async def search(...)` if it does async I/O).
