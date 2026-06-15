# books-agent — "Talk to your books"

A natural-language book recommender. Ask in plain language ("90s books about car
chases", "something melancholic about memory and loss", "sci-fi with a strong
female lead") and get a short ranked list with a one-line justification per pick.

## Contents

- [A meaningful use of Artificial Intelligence](#a-meaningful-use-of-artificial-intelligence)
- [Architecture and Domain-Driven Design](#architecture-and-domain-driven-design)
- [Built with Claude Code Skills](#built-with-claude-code-skills)
- [Retrieval design](#retrieval-design)
- [Tech stack](#tech-stack)
- [Running the project](#running-the-project)
- [Key trade-offs](#key-trade-offs)

## A meaningful use of Artificial Intelligence

The agent combines two retrieval modes, each suited to a different kind of question:

- **Structured filtering** (decade, rating, author, category) → **text-to-SQL over PostgreSQL**.
- **Semantic search** over book descriptions → **vector similarity in Weaviate**.

An LLM router (`classify_intent`) decides `STRUCTURED` / `SEMANTIC` / `HYBRID` and
emits a read-only SQL filter and/or a rewritten semantic query. On **HYBRID** the
SQL filter runs first to produce a candidate set (an `isbn13` allowlist), then a
**filtered** vector search ranks _within_ that set, and an LLM reranks and
justifies the top picks. Pure SQL can't answer "melancholic about memory"; pure
embeddings lose exact filters like decade or rating — the hybrid is the value.

The generated SQL is surfaced in the UI for transparency, and a failed query gets
**one LLM repair retry** before degrading gracefully.

## Architecture and Domain-Driven Design

<a href="https://www.amazon.com.br/gp/product/B0F6C97JWL">
  <img src="docs/clean_architecture_with_python.jpg" alt="Clean Architecture with Python — Sam Keen" width="150" align="right"/>
</a>

This backend is a deliberate application of **Clean Architecture / Domain-Driven
Design**, following the layering and dependency discipline of
[**Clean Architecture with Python**](https://www.amazon.com.br/gp/product/B0F6C97JWL)
(Sam Keen, Packt, 2025).

**The dependency rule — inward only.** Outer layers depend on inner layers, never
the reverse. The `domain` has _zero_ framework imports; the `application` layer
never imports FastAPI, SQLModel, or LangGraph. Anything volatile (the web
framework, the database, the LLM, the vector store, the agent framework) lives in
an outer ring behind an interface the inner layers own — so it can be swapped or
tested in isolation. The architecture lives in the inner layers; the frameworks
stay replaceable at the edges.

```text
        Interfaces                 Agent (LangGraph)
   (controllers / presenters)      (graph + nodes)        ← outer adapter rings (peers)
              \                       /
               ▼                     ▼
                    Application                  ← use cases · ports · Result · UoW · DTOs
                        ▼
                      Domain                     ← entities · value objects · exceptions

   Infrastructure ── implements every port; the composition root wires the rings ──
```

### Domain — `backend/app/domain/`

Pure business model; no framework imports. The innermost ring.

- **Entities** (identity, mutable): `Entity` (UUID base), `UserDomain`, and
  `BookDomain` — a book is identified by its `isbn13` natural key.
- **Value objects** (immutable, equality by value): `Email` (self-validating in
  `__post_init__`), plus the `StrEnum`s `UserRole` and `Intent`. `Intent`
  (`STRUCTURED` / `SEMANTIC` / `HYBRID`) is the **ubiquitous-language** term the
  whole graph routes on.
- **Domain exceptions**: `DomainError`, `UserIdNotFoundError`.

### Application — `backend/app/application/`

Orchestrates the domain to fulfil use cases. Knows nothing about HTTP, SQL, or
LangGraph — it speaks only in **ports** (interfaces it defines and owns).

- **Use case**: `AnswerBookQuestionUseCase` — opens the Unit of Work, delegates to
  the recommender port, and returns a `Result`.
- **Ports & adapters (Hexagonal).** _Capability_ ports in `service_ports/`
  (`LLMService`, `EmbeddingsService`, `BookRecommenderPort`, `PasswordHasher`,
  `TokenService`); _data-access_ ports in `repositories/` (`BookRepository`,
  `BookVectorRepository`, `UserRepository`). The application depends on these
  abstractions; concrete adapters live further out.
- **`Result[T]` / `Error` / `ErrorCode`** — each use case returns its success or
  failure to the caller as an explicit value.
- **`UnitOfWork` protocol** — the transactional boundary that exposes repositories;
  Pydantic **DTOs** carry data across the boundary.

### Interfaces — `backend/app/interfaces/`

Adapts application output into a delivery shape; never raises HTTP itself.
Controllers (`BookController`), presenters (`BookPresenter` → `WebBookPresenter`),
and view models wrapped in `OperationResult`.

### Infrastructure — `backend/app/infra/`

Concrete adapters and technical detail. Depends on the inner layers; nothing inner
depends on it.

- **Persistence**: `BookPostgreRepository` (with the SELECT-only SQL guard),
  SQLModel models + mappers.
- **External services**: OpenAI (`llm/`, `embeddings/`), Weaviate (`vector/`).
- **Web + composition root**: the FastAPI app factory whose `lifespan` is the
  **composition root** — it wires each port to a concrete adapter; plus the
  `Depends` DI graph and the `ErrorCode`→HTTP mapping.

### Agent — `backend/app/agent/` (the distinctive ring)

The LangGraph package is modeled as an **outer adapter ring, a peer of `infra/`**.
Its nodes depend only on application ports (never on `infra`); the compiled graph
**implements `BookRecommenderPort`**; and concrete clients are injected via
`RunnableConfig` at the composition root. LangGraph wants a flat
`nodes/state/tools` layout — modeling it as an adapter ring absorbed that
opinionated framework **without breaking the dependency rule**, a concrete case of
treating frameworks as a detail.

![LangGraph recommendation graph](docs/agent-graph.png)

> Rendered from the compiled graph via `build_graph().get_graph().draw_mermaid_png()`.

Graph state is checkpointed with `MemorySaver` keyed by `thread_id` (conversation
plumbing; history-aware follow-ups are a documented later extension).

### How the book's principles show up here

- **Dependency rule** — `domain` imports nothing outward; enforced by package layout.
- **Entities vs value objects** — `BookDomain` (identity) vs `Email` / `Intent` (value).
- **Ports & adapters** — `service_ports/` + `repositories/` define interfaces; `infra/` + `agent/` implement them.
- **Use-case orchestration** — `AnswerBookQuestionUseCase` coordinates; it holds no I/O.
- **Repository + Unit of Work** — data access behind `BookRepository`, transactions behind `UnitOfWork`.
- **`Result` over exceptions** — `Result[T]` makes the success/failure contract explicit.
- **Frameworks as a detail** — FastAPI, SQLModel, Weaviate, and LangGraph all sit in swappable outer rings.

See [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) for the full design and
[CLAUDE.md](CLAUDE.md) for the architecture rules.

## Built with Claude Code Skills

The project was developed with a set of custom **Claude Code Skills** —
versioned playbooks under [`.claude/skills/`](.claude/skills/) that feed the
project's conventions to the AI assistant on demand. They paid off twice: the
house patterns were already known to the assistant, so features were delivered
**faster** with less re-explaining and rework; and every new layer was generated
against the **same Clean Architecture / DDD rules**, so the codebase stayed
consistent instead of drifting into ad-hoc shapes.

| Skill | Encodes | Used here for |
| --- | --- | --- |
| **`fastapi-conventions`** | The backend's Clean Architecture / DDD rules — routes, controllers, use cases, DTOs, repositories, entities, Unit of Work, presenters, DI wiring. | Generating the book-recommendation slice (controller → use case → ports → repository → presenter) so it matched the existing `users` / `auth` slices exactly. |
| **`langgraph-agent`** | Production LangGraph conventions — state & reducers, thin node functions, dependency injection via `RunnableConfig`, structured output, conditional-edge routing, the deploy contract. | Designing the `agent/` package: the state shape, the `classify → sql → semantic → rank` graph, routing, and keeping nodes free of concrete clients. |
| **`grill-me`** | An interview loop that stress-tests a plan, resolving each design decision one branch at a time. | The pre-build design review that locked the open decisions — text-to-SQL + guard, sequential HYBRID, OpenAI, PostgreSQL over DuckDB, and the conversation-memory scope. |

The skills are checked into the repo, so the conventions travel with the codebase
and stay reproducible for the next contributor.

## Retrieval design

The heart of the project is **how the two retrieval modes divide the work**.
Guiding principle: _exact constraints belong in SQL (precise, auditable); meaning
belongs in embeddings._ Each question is routed to whichever half — or both — can
actually answer it.

### What is embedded

Only the book **`description`** is vectorized (OpenAI `text-embedding-3-small`,
1536-dim). Title, author, categories, year, rating, etc. are stored in Weaviate as
scalar **properties** _next to_ the vector — so a semantic hit can return full book
data without a second DB call — but they do **not** influence similarity. So
"melancholic about memory and loss" is matched against description text only.

### Division of labour

| Query dimension | Engine | Mechanism |
| --- | --- | --- |
| mood / theme / subject | **Weaviate** | vector similarity (`near_vector`) over the description embedding |
| decade / year, rating, author, category | **PostgreSQL** | LLM-generated `SELECT … WHERE …` (text-to-SQL) |
| "restrict to these books" (HYBRID only) | **Weaviate** | an `isbn13` filter (`contains_any`) that constrains the vector search |

Weaviate is deliberately **not** used for attribute filtering (year/rating/author),
even though it could be — that is PostgreSQL's job, so the structured filter stays
exact, auditable, and is surfaced to the user as the **generated SQL**. The only
Weaviate filter we build is the `isbn13` allowlist that glues the two halves
together on the hybrid path.

### How a query flows

`classify_intent` routes to one of three paths:

- **STRUCTURED** — "90s sci-fi rated above 4" → PostgreSQL only; Weaviate untouched.
- **SEMANTIC** — "something melancholic about memory" → Weaviate `near_vector` only, no filter.
- **HYBRID** — "90s books about car chases" → SQL runs **first** to get the candidate `isbn13` set, then a **filtered** `near_vector` ranks semantically _within_ that set.

### Worked example — the HYBRID path

> "upbeat 90s fantasy with a strong female lead"

1. **`classify_intent`** → `HYBRID`; emits SQL (`… WHERE published_year BETWEEN 1990 AND 1999 AND categories ILIKE '%fantasy%'`) **and** a semantic query (`"upbeat adventure, strong female protagonist"`).
2. **`sql_search`** runs the SQL on PostgreSQL → the books passing the hard filter; their `isbn13`s become the **allowlist**.
3. **`semantic_search`** embeds the semantic query and asks Weaviate for the nearest descriptions **restricted to that allowlist** → the decade/genre constraint is guaranteed; the _ordering_ is by meaning.
4. **`rank`** (LLM) reranks the survivors and writes a one-line justification each.

Pure SQL can't rank "upbeat / strong female lead" — there's no such column. Pure
embeddings would happily return an 80s book or a poorly-rated one. The hybrid gets
both right, and that separation is the whole value proposition.

## Tech stack

- **Backend:** Python 3.13, FastAPI, LangGraph, SQLModel/asyncpg (PostgreSQL),
  weaviate-client (Weaviate), `langchain-openai` (chat + embeddings), `uv`.
- **AI:** OpenAI chat model (classify / repair / rank) + `text-embedding-3-small`.
- **Frontend:** React + Vite (query box, intent badge, SQL transparency panel, ranked cards).

## Running the project

**Prerequisites:** Python 3.13 + [`uv`](https://docs.astral.sh/uv/), Node 18+,
Docker (for Weaviate), a running PostgreSQL, and an OpenAI API key.

### 1. Create the PostgreSQL database

The default `DATABASE_URL` points at a database named `books`:

```bash
createdb books            # or: psql -c "CREATE DATABASE books;"
```

### 2. Start Weaviate (vector store)

From the repo root:

```bash
docker compose up -d weaviate
# ready check: curl http://localhost:8080/v1/.well-known/ready
```

### 3. Configure and migrate the backend

```bash
cd backend
cp .env.example .env       # then edit .env:
                           #  - OPENAI_API_KEY=sk-...        (required)
                           #  - OPENAI_CHAT_MODEL=...        (your model id)
                           #  - DATABASE_URL=...             (matches step 1)
                           #  - leave LANGCHAIN_TRACING_V2 unset unless you have a key
uv sync                    # install dependencies into .venv
uv run alembic upgrade head   # create the users + books tables
```

### 4. Load the dataset

Cleans `books.csv` → loads PostgreSQL → embeds descriptions → seeds Weaviate.
Idempotent (safe to re-run); run from `backend/`:

```bash
uv run python scripts/prepare_data.py
```

### 5. Run the backend

```bash
uv run python main.py          # http://localhost:8000  (Swagger UI at /docs)
# equivalently: uv run uvicorn main:app --reload --port 8000
```

### 6. Run the frontend (separate terminal)

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173 (proxies /books → :8000)
```

### Try it from the command line

```bash
curl -X POST http://localhost:8000/books/recommendations \
  -H "Content-Type: application/json" \
  -d '{"question": "90s books about car chases"}'
```

### Run the tests

```bash
cd backend && uv run pytest    # SQL guard + node/router tests (no network needed)
```

## Key trade-offs

- **Text-to-SQL** (vs. a structured-filter builder): more genuinely "AI" and
  matches the brief's "show the SQL" + "retry" requirements, but the
  LLM-generated SQL needs a hard guard. We run a **SELECT-only guard** (rejects
  non-SELECT/multi-statement/comments) + forced `LIMIT` + `statement_timeout`
  inside the repository adapter, on the **same engine** as the app (no separate
  read-only role). The guard is the only write-protection, so it is unit-tested.
- **Sequential HYBRID** (vs. parallel fan-out): we give up parallel-execution
  latency for a cleaner filter-constrained ranking (Weaviate filtered ANN over
  the SQL allowlist).
- **OpenAI** for chat + embeddings (overrides the brief's Anthropic note);
  Weaviate via **Docker** (Embedded is unsupported on Windows).
- **Conversation memory** is plumbing only (checkpointer + `thread_id`); the
  classifier reads just the current question for now.
