# books-agent — "Talk to your books"

A natural-language book recommender. Ask in plain language ("90s books about car
chases", "something melancholic about memory and loss", "sci-fi with a strong
female lead") and get a short ranked list with a one-line justification per pick.

## Why the AI is meaningful

The agent combines two retrieval modes instead of being a thin LLM wrapper:

- **Structured filtering** (decade, rating, author, category) → **text-to-SQL over PostgreSQL**.
- **Semantic search** over book descriptions → **vector similarity in Weaviate**.

An LLM router (`classify_intent`) decides `STRUCTURED` / `SEMANTIC` / `HYBRID` and
emits a read-only SQL filter and/or a rewritten semantic query. On **HYBRID** the
SQL filter runs first to produce a candidate set (an `isbn13` allowlist), then a
**filtered** vector search ranks *within* that set, and an LLM reranks and
justifies the top picks. Pure SQL can't answer "melancholic about memory"; pure
embeddings lose exact filters like decade or rating — the hybrid is the value.

The generated SQL is surfaced in the UI for transparency, and a failed query gets
**one LLM repair retry** before degrading gracefully.

## Architecture

FastAPI backend in **Clean Architecture / DDD** (dependencies point inward only:
`domain ← application ← infra`/`interfaces`). The LangGraph package
(`backend/app/agent/`) is an **outer adapter ring**, a peer of `infra/`: its nodes
depend only on application ports, with concrete clients injected via
`RunnableConfig`. The compiled graph implements `BookRecommenderPort`; the use
case depends on that port and returns the project's `Result`.

```text
question ─▶ classify_intent ─▶ (STRUCTURED|HYBRID) ─▶ sql_search ─▶ (HYBRID) ─▶ semantic_search ─▶ rank ─▶ answer
                            └▶ (SEMANTIC) ───────────────────────────────────▶ semantic_search ─┘
                                                         └▶ (error, once) ─▶ repair_sql ─▶ sql_search
```

![LangGraph recommendation graph](docs/agent-graph.png)

> Rendered from the compiled graph via `build_graph().get_graph().draw_mermaid_png()`.

Graph state is checkpointed with `MemorySaver` keyed by `thread_id` (conversation
plumbing; history-aware follow-ups are a documented later extension).

See [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) for the full design and
[CLAUDE.md](CLAUDE.md) for the architecture rules.

## Tech stack

- **Backend:** Python 3.13, FastAPI, LangGraph, SQLModel/asyncpg (PostgreSQL),
  weaviate-client (Weaviate), `langchain-openai` (chat + embeddings), `uv`.
- **AI:** OpenAI chat model (classify / repair / rank) + `text-embedding-3-small`.
- **Frontend:** React + Vite (query box, intent badge, SQL transparency panel, ranked cards).

## Setup

Prereqs: Python 3.13 + `uv`, Node 18+, Docker, a running PostgreSQL, an OpenAI API key.

```bash
# 1. Vector store
docker compose up -d weaviate

# 2. Backend
cd backend
cp .env.example .env          # fill OPENAI_API_KEY, DATABASE_URL, etc.
uv sync
uv run alembic upgrade head   # creates users + books tables

# 3. Load the dataset (clean CSV → PostgreSQL → embed → Weaviate). Idempotent.
uv run python scripts/prepare_data.py

# 4. Run the API
uv run uvicorn app.main:app --reload   # http://localhost:8000/docs

# 5. Frontend (separate terminal)
cd ../frontend
npm install && npm run dev    # http://localhost:5173 (proxies /books to :8000)
```

### Try it

```bash
curl -X POST http://localhost:8000/books/recommendations \
  -H "Content-Type: application/json" \
  -d '{"question": "90s books about car chases"}'
```

## Tests

```bash
cd backend && uv run pytest        # SQL guard + node/router tests (no network)
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
