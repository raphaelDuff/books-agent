# Pitfalls

The short list of mistakes that break LangGraph graphs — often silently. Skim before
shipping any graph change.

## State

- **Mutating `state` in place** instead of returning a partial dict. Reducers won't run and
  parallel writes corrupt each other. Always `return {"key": value}`.
- **Missing reducer on an accumulating key.** Two nodes write `messages` with no
  `add_messages` reducer → the second overwrites the first. If any two nodes write the same
  key, that key needs a reducer (or split into two keys).
- **Returning the whole state** from a node. Return only changed keys.
- **Non-serializable objects in state** (DB connections, clients). Breaks the checkpointer.
  Those go in config, not state.

## Routing

- **Router return value not in the mapping dict.** Typo or unhandled branch → routes
  nowhere, graph errors. Keep the mapping exhaustive over the router's outputs.
- **Listing the list in the mapping.** When a router returns `["a", "b"]` for parallel
  fan-out, the mapping lists `a` and `b` individually, not the list.
- **Parallel nodes writing the same key without a reducer** (see State). The HYBRID path is
  the usual offender — write to separate keys and merge.

## Construction & compile

- **Forgetting to compile.** `StateGraph` must be `.compile()`d before `.invoke()`. The
  thing you export in `agent.py` is the compiled graph (or a builder function the platform
  compiles).
- **Compiling with a checkpointer when deploying to LangGraph Platform.** The platform
  injects persistence; passing your own `MemorySaver` conflicts. Compile _without_ a
  checkpointer for platform deploy; pass one only for local/embedded runs.
- **No `thread_id` when a checkpointer is set.** A checkpointer needs
  `config={"configurable": {"thread_id": "..."}}` to know which conversation to persist.

## Dependencies

- **Module-level clients** (`llm = ChatOpenAI()` at top of a node file). Runs at import,
  unmockable, binds the graph to one vendor. Inject via config or `functools.partial`.
- **Putting `with_structured_output` in the node** instead of the adapter. Leaks LangChain
  types into the orchestration layer and makes the node hard to test. Keep it in the port
  implementation.

## Async

- **Blocking I/O inside an `async def` node.** A sync `requests.get` / blocking DB call
  under an async graph stalls the event loop. Either make the node sync, or use an async
  client and `await` it.

## Versioning

- **Assuming an API that moved.** LangGraph changes faster than most libraries. This skill
  targets `langgraph >= 0.2`. If `config_schema`, `Send`, or import paths differ in the
  installed version, check the installed package before generating code rather than trusting
  these snippets verbatim.
